import inspect
import logging
import os
import requests

COMPUTEX_PASSWORD = os.environ.get("COMPUTEX_PASSWORD")
COMPUTEX_USERNAME = os.environ.get("COMPUTEX_USERNAME")
URL = "https://api.computex.co/api/v1"

logger = logging.getLogger("virtual_server")
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


class Deployment:
    def deploy_serverless_app(
        self,
        headers,
        app_name,
        container_image,
        model_image,
        num_cpu_cores,
        num_gpu,
        memory,
        container_concurrency=1,
        min_scale=0,
        max_scale=1,
        secrets={},
        is_public=False,
    ):
        """Deploy a serverless app.

        This deployment type is autoscaling and is suitable for apps that need to scale up and down quickly.
        """

        spec = {
            "app_name": app_name,
            "container_image": container_image,
            "model_image": model_image,
            "num_cpu_cores": num_cpu_cores,
            "num_gpu": num_gpu,
            "memory": memory,
            "container_concurrency": container_concurrency,
            "min_scale": min_scale,
            "max_scale": max_scale,
            "secrets": secrets,
            "is_public": is_public,
        }

        response = requests.post(
            f"{URL}/deployments/deploy_serverless",
            headers=headers,
            json=spec,
        )
        formatted_response = format_response(response)
        return formatted_response

    def deploy_hot_replica(
        self,
        headers,
        app_name,
        container_image,
        model_image,
        num_cpu_cores,
        num_gpu,
        memory,
        secrets={},
        is_public=False,
    ):
        """Deploy a hot replica app.

        This deployment type is suitable for apps that have fixed workloads and do not need scaling
        """

        spec = {
            "app_name": app_name,
            "container_image": container_image,
            "model_image": model_image,
            "num_cpu_cores": num_cpu_cores,
            "num_gpu": num_gpu,
            "memory": memory,
            "secrets": secrets,
            "is_public": is_public,
        }

        response = requests.post(
            f"{URL}/deployments/deploy_serverless",
            headers=headers,
            json=spec,
        )
        formatted_response = format_response(response)
        return formatted_response

    def get_deployments(self, headers):
        """Get the list of deployments"""
        response = requests.get(f"{URL}/deployments", headers=headers)
        formatted_response = format_response(response)
        return formatted_response

    def get_logs(self, deployment_id, headers):
        """Get the logs for a deployment"""
        response = requests.get(
            f"{URL}/deployments/{deployment_id}/logs", headers=headers
        )
        formatted_response = format_response(response)
        return formatted_response

    def delete_deployment(self, deployment_id, headers, is_serverless=False):
        """Delete the deployment"""
        response = requests.delete(
            f"{URL}/deployments/{deployment_id}?is_serverless={is_serverless}",
            headers=headers,
        )
        logger.info(f"Delete response: {response}")
        return response


def main(deployment_specs):
    authentication = Authentication()
    deployment = Deployment()
    token = authentication.log_in(COMPUTEX_USERNAME, COMPUTEX_PASSWORD)
    headers = authentication.generate_headers(token)

    # Deploy a serverless, autoscaling app
    deployment.deploy_serverless_app(
        headers,
        app_name=deployment_specs["app_name"],
        container_image=deployment_specs["container_image"],
        model_image=deployment_specs["model_image"],
        num_cpu_cores=deployment_specs["num_cpu_cores"],
        num_gpu=deployment_specs["num_gpu"],
        memory=deployment_specs["memory"],
        container_concurrency=deployment_specs["container_concurrency"],
        min_scale=deployment_specs["min_scale"],
        max_scale=deployment_specs["max_scale"],
        secrets=deployment_specs["secrets"],
        is_public=deployment_specs["is_public"],
    )

    #####################################
    # Uncomment the following lines to access the other endpoints
    #####################################

    # List all deployments
    # response = deployment.get_deployments(headers)

    # Get the logs for a deployment
    # response = deployment.get_logs(
    #    deployment_specs["app_name"], headers
    # )

    # Delete a deployment
    deployment.delete_deployment(deployment_specs["app_name"], headers)


if __name__ == "__main__":
    if not COMPUTEX_USERNAME or not COMPUTEX_PASSWORD:
        raise Exception(
            "Please set the COMPUTEX_USERNAME and COMPUTEX_PASSWORD environment variables."
        )

    # Enter your deployment specs here
    deployment_specs = {
        "app_name": "your-app-name",
        "container_image": "registry-dev.computex.ai/your-org/image-with-predict-logic",
        "model_image": "registry-dev.computex.ai/your-org/your-org/image-with-logic-for-downloading-model",
        "num_cpu_cores": 4,
        "num_gpu": 0,
        "memory": 8,
        "container_concurrency": 1,
        "min_scale": 0,
        "max_scale": 10,
        "secrets": {},
        "is_public": False,
    }

    main(deployment_specs)
