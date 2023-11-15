import inspect
import logging
import os
import requests
import time

COMPUTEX_PASSWORD = os.environ.get("COMPUTEX_PASSWORD")
COMPUTEX_USERNAME = os.environ.get("COMPUTEX_USERNAME")
URL = "https://api.computex.ai/api/v1"
ORG_NAME = os.environ.get("ORG_NAME")


logger = logging.getLogger("prediction")
logging.basicConfig(level=logging.INFO)


def format_response(response):
    """Format the response"""
    caller_name = inspect.currentframe().f_back.f_code.co_name
    if 200 <= response.status_code < 300:
        logger.info(f"{caller_name} succeeded.")
        logger.debug(f"{caller_name} response: ", response.json())
        return response.json()
    else:
        logger.error(
            f"{caller_name} failed. Response code: {response.status_code}, message: {response.text}"
        )
        return {"error": response.status_code, "message": response.text}


class Authentication:
    @staticmethod
    def log_in(username, password):
        # Log in to get a JWT token (expires in 12 hours)
        response = requests.post(
            f"{URL}/users/login",
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json={"email": username, "password": password},
        )
        if response.status_code != 200:
            raise Exception("Log in failed.")
        token = response.json()["token"]
        return token

    @staticmethod
    def generate_headers(token):
        headers = {"accept": "application/json", "Authorization": f"Bearer {token}"}
        return headers


class Prediction:
    @staticmethod
    def predict(payload, headers, app_name="salesforce-xgen-7b-8k-base-model"):
        """Create a virtual server"""
        logger.info(f"{URL}/predictions/{ORG_NAME}/{app_name}/predict")
        response = requests.post(
            f"{URL}/predictions/{app_name}/predict",
            headers=headers,
            json=payload,
        )
        logger.info(f"response: {response}")
        return response

    @staticmethod
    def get_prediction(prediction_id, headers):
        """Delete the virtual server"""
        response = requests.get(
            f"{URL}/predictions/prediction/{prediction_id}",
            headers=headers,
        )
        return response

    @staticmethod
    def download_prediction_from_url(url):
        """Download the prediction from the url"""
        result_response = requests.get(url)
        result_response.raise_for_status()
        prediction_result = result_response.json()

        return prediction_result


def main(app_name="xgen-7b-8k-base-model", prompt="Please input some text"):
    authentication = Authentication()
    token = authentication.log_in(COMPUTEX_USERNAME, COMPUTEX_PASSWORD)
    headers = authentication.generate_headers(token)

    prediction = Prediction()

    response = prediction.predict(
        {
            "prompt": prompt,
            "max_length": 500,
            "top_p": 0.95,
            "top_k": 1,
            "temperature": 0.75,
            "num_return_sequences": 1,
        },
        headers,
        app_name,
    )

    prediction_id = response.json()["prediction_id"]
    logger.info(f"prediction_id: {prediction_id}")

    while True:
        response = prediction.get_prediction(prediction_id, headers)
        if response.json()["status"] == "success":
            presigned_url = response.json()["presigned_url"]
            prediction_response = Prediction.download_prediction_from_url(presigned_url)

            logger.info(prediction_response)
            break

        logger.info(response.json())
        time.sleep(10)


if __name__ == "__main__":
    if not COMPUTEX_USERNAME or not COMPUTEX_PASSWORD:
        raise Exception(
            "Please set the COMPUTEX_USERNAME and COMPUTEX_PASSWORD environment variables."
        )

    if not ORG_NAME:
        raise Exception("Please set the ORG_NAME environment variable.")

    main(app_name="dummy-test")
