"""Update this file to include logic to run inference on a model.

The input_params and input_file are passed to the Predictor class from the app.py file

"""

# import tempfile
from fastapi import File, UploadFile

import cv2
import numpy as np
import os
from ultralytics import YOLO

MODEL_PATH = 'pothole-detector-model.pt'

def write_binary_to_file(filename: str, binary: np.ndarray) -> None:
    """Write binary data to file."""
    file_path = os.path.join("/tmp", filename)
    with open(file_path, 'wb') as f:
        f.write(binary)

    return file_path


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
        self.model = YOLO(MODEL_PATH)

    def process(self):
        """Process the input data and run the model inference.

        To handle different types of inputs, you might need to modify this method. 
        For example, if your model requires images as input, you would need to decode the input file as an image. 
        If your model requires a text input, you might need to read the input file as a text file.

        Similarly, the output of your model might be different depending on the model you run. 
        Make sure to adjust the return value of this method to match the output of your model.

        return: The result of the model inference.
        """
        image_path = write_binary_to_file(self.input_file.filename, self.input_file.file.read())
        image = cv2.imread(image_path)

        if image is None:
            return

        outputs = self.model.predict(source=image_path)
        bounding_boxes = outputs[0].cpu().numpy()

        for bounding_box in bounding_boxes.boxes.xyxy:
            box_start = (int(bounding_box[0]), int(bounding_box[1]))
            box_end = (int(bounding_box[2]), int(bounding_box[3]))

            cv2.rectangle(
                image,
                box_start,
                box_end,
                color=(0, 0, 255),
                thickness=2,
                lineType=cv2.LINE_AA
            )

        # Encode the image as a binary
        _, buffer = cv2.imencode('.jpg', image)
        img_binary = np.array(buffer).tobytes()

        return img_binary

    async def infer(self):
        """Run the inference process and return the result.

        This method is called by the /infer endpoint to run the model inference.
        """
        response = self.process()
        return response
