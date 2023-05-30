"""API Router. Defines the API endpoints and their corresponding handlers.

No need to edit this file.
"""
import io
import json
import os

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from inference import Predictor

app = FastAPI()

# This FastAPI application serves a machine learning model for inference.
# It provides an endpoint, /infer, which accepts POST requests with an input_file and optional parameters.

# The /infer endpoint processes the input file and parameters using the Predictor class defined in inference.py.
# It returns the result of the inference as a file, a string, or a JSON object depending on the output of the inference.


def parse_input_params(params: str = Form(...)):
    """Parse input params passed as a string

    Input Format: '[{"name": "param1", "value": "value1"}, {"name": "param2", "value": "value2"}]'

    Output Format: {"param1": "value1", "param2": "value2"}
    """
    if not params:
        return {}
    try:
        input_params = json.loads(params)

        # Confirm that the input params are a list of dicts
        if not isinstance(input_params, list) or not all(isinstance(item, dict) for item in input_params):
            raise ValueError(
                "Invalid params format. Expected a JSON array of objects.")

        for item in input_params:
            if "name" not in item or "value" not in item:
                raise ValueError(
                    "Invalid params format. Each object must have a 'name' and 'value' attribute.")

        # Convert the list of dicts to a dict
        input_params_dict = {item["name"]: item["value"]
                             for item in input_params}

    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(
            "Invalid params format. Expected a JSON array of objects. Details: " + str(e))

    return input_params_dict


@app.post("/infer")
async def infer(
    input_file: UploadFile = File(None, description="Optional input file."),
    params: str = Form(
        None, description='Input format (use double quotes): [{"name": "param1", "value": "value1"}, {"name": "param2", "value": "value2"}]'),

):
    """Main inference endpoint."""
    input_params = parse_input_params(params)

    try:
        predictor = Predictor(input_params=input_params, input_file=input_file)
        result = await predictor.infer()

        if isinstance(result, str):
            if os.path.isfile(result):
                return FileResponse(result)
            return result

        if isinstance(result, (dict, bool, float)):
            return result

        if isinstance(result, bytes):
            return StreamingResponse(io.BytesIO(result), media_type="application/octet-stream")

        return JSONResponse(content={'message': 'Inference failed'}, status_code=500)
    except Exception as exception:
        return JSONResponse(content={'message': str(exception)}, status_code=500)


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"Health": "GOOD"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
