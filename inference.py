"""Update this file to include logic to run inference on a model.

The input_params and input_file are passed to the Predictor class from the app.py file

"""

# import tempfile
from fastapi import File, UploadFile


class Predictor:
    """ Class for running inference on a model.

    This class is initialized with parameters and an optional input file from the /infer endpoint.
    It processes the input data and runs it through a machine learning model to produce the inference
    result.
    """

    def __init__(
            self,
            input_params: dict,
            input_file: UploadFile = File(
                None, description="Optional input file.")
    ):
        """Initialize the Predictor class with inputs from the /infer endpoint.
        """
        self.input_params = input_params
        self.input_file = input_file

    def process(self):
        """Process the input data and run the model inference.

        To handle different types of inputs, you might need to modify this method. 
        For example, if your model requires images as input, you would need to decode the input file as an image. 
        If your model requires a text input, you might need to read the input file as a text file.

        Similarly, the output of your model might be different depending on the model you run. 
        Make sure to adjust the return value of this method to match the output of your model.

        return: The result of the model inference.
        """

        # load model

        # run inference
        result = self.input_file.file.read()

        return result

    async def infer(self):
        """Run the inference process and return the result.

        This method is called by the /infer endpoint to run the model inference.
        """
        response = self.process()
        return response
