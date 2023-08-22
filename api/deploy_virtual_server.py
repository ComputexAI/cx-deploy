import inspect
import logging
import os
import requests
import time

COMPUTEX_PASSWORD = os.environ.get("COMPUTEX_PASSWORD")
COMPUTEX_USERNAME = os.environ.get("COMPUTEX_USERNAME")
URL = "https://api.computex.co/api/v1"


# Set the username and password to your desired config
VIRTUAL_SERVER_USERNAME = "username"
VIRTUAL_SERVER_PASSWORD = "password"


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
        logger.error(f"{caller_name} failed. Response code: {response.status_code}, message: {response.text}")
        return {"error": response.status_code, "message": response.text}


def generate_1x_rtx_A5000_build_spec(username, password):
    timestamp = int(time.time())
    virtual_server_name = f"1x_RTX_A5000-{timestamp}"

    logger.info(f"virtual_server_name: {virtual_server_name}")

    spec = {
        "name": virtual_server_name,
        "num_cpu_cores": 4,
        "num_gpu": 1,
        "gpu_sku": "RTX_A5000",
        "memory": 24,
        "storage_size_in_GiB": 100,
        "username": username,
        "password": password,
    }
    return spec


def generate_4x_rtx_a5000_build_spec(username, password):
    timestamp = int(time.time())
    virtual_server_name = f"4x-rtx-a5000-{timestamp}"

    logger.info(f"virtual_server_name: {virtual_server_name}")

    spec = {
        "name": virtual_server_name,
        "num_cpu_cores": 32,
        "num_gpu": 4,
        "gpu_sku": "RTX_A5000",
        "memory": 244,
        "storage_size_in_GiB": 300,
        "username": username,
        "password": password,
    }
    return spec


def generate_8x_rtx_a6000_build_spec(username, password):
    timestamp = int(time.time())
    virtual_server_name = f"8x-rtx-a6000-{timestamp}"

    logger.info(f"virtual_server_name: {virtual_server_name}")

    spec = {
        "name": virtual_server_name,
        "num_cpu_cores": 96,
        "num_gpu": 8,
        "gpu_sku": "RTX_A6000",
        "memory": 696,
        "storage_size_in_GiB": 300,
        "username": username,
        "password": password,
    }
    return spec


class Authentication:

    @staticmethod
    def log_in(username, password):
        # Log in to get a JWT token (expires in 12 hours)
        response = requests.post(
            f"{URL}/users/login",
            headers={"accept": "application/json",
                     "Content-Type": "application/json"
                     },
            json={"email": username, "password": password},
        )
        if response.status_code != 200:
            raise Exception("Log in failed.")
        token = response.json()["token"]
        return token

    @staticmethod
    def generate_headers(token):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        return headers


class VirtualServer:

    @staticmethod
    def create_virtual_server(build_specs, headers):
        """Create a virtual server"""
        response = requests.post(
            f"{URL}/virtual-servers",
            headers=headers,
            json=build_specs,
        )
        formatted_response = format_response(response)
        return formatted_response

    @staticmethod
    def delete_virtual_server(virtual_server_id, headers):
        """Delete the virtual server"""
        response = requests.delete(
            f"{URL}/virtual-servers/{virtual_server_id}",
            headers=headers,
        )
        logger.info(f"Delete response: {response}")
        return response

    @staticmethod
    def list_virtual_servers(headers):
        """Print the list of active virtual servers"""
        response = requests.get(
            f"{URL}/virtual-servers",
            headers=headers,
        )
        formatted_response = format_response(response)
        return formatted_response

    @staticmethod
    def get_virtual_server(virtual_server_id, headers):
        """Print the build spec of the virtual server"""
        response = requests.get(
            f"{URL}/virtual-servers/{virtual_server_id}",
            headers=headers,
        )
        formatted_response = format_response(response)
        return formatted_response

    @staticmethod
    def get_virtual_server_status(virtual_server_id, headers):
        """Print the status of the virtual server"""
        response = requests.get(
            f"{URL}/virtual-servers/{virtual_server_id}/status",
            headers=headers,
        )
        formatted_response = format_response(response)
        return formatted_response


def deploy_virtual_servers(headers):
    """Deploy two virtual servers spec'd out for Narya"""

    build_spec_1x_rtx_a5000 = generate_1x_rtx_A5000_build_spec(VIRTUAL_SERVER_USERNAME, VIRTUAL_SERVER_PASSWORD)
    VirtualServer.create_virtual_server(build_spec_1x_rtx_a5000, headers)
    time.sleep(100)
    get_external_ip(headers, build_spec_1x_rtx_a5000["name"])

    # Deploy smaller virtual server
    # build_spec_4x_rtx_a5000 = generate_4x_rtx_a5000_build_spec(VIRTUAL_SERVER_USERNAME, VIRTUAL_SERVER_PASSWORD)
    # VirtualServer.create_virtual_server(build_spec_4x_rtx_a5000, headers)
    # time.sleep(100)
    # get_external_ip(headers, build_spec_4x_rtx_a5000["name"])

    # Deploy larger virtual server
    # build_spec_8x_rtx_a6000 = generate_8x_rtx_a6000_build_spec(VIRTUAL_SERVER_USERNAME, VIRTUAL_SERVER_PASSWORD)
    # VirtualServer.create_virtual_server(build_spec_8x_rtx_a6000, headers)
    # time.sleep(100)
    # get_external_ip(headers, build_spec_8x_rtx_a6000["name"])


def get_external_ip(headers, name):
    """Get the external IP address of the virtual server to SSH into"""
    response = VirtualServer.get_virtual_server_status(name, headers)
    try:
        external_ip = response["status"]["network"]["externalIP"]
        logger.info(f"SSH into {name} with the following command: `$ ssh {VIRTUAL_SERVER_USERNAME}@{external_ip}`")
    except KeyError:
        logger.info("Could not get IP address. Check the status of the virtual server.")


def main():
    authentication = Authentication()
    token = authentication.log_in(COMPUTEX_USERNAME, COMPUTEX_PASSWORD)
    headers = authentication.generate_headers(token)

    # Deploy the virtual servers
    deploy_virtual_servers(headers)

    #####################################
    # Uncomment the following lines to access the other endpoints
    #####################################

    # List all virtual servers
    # response = VirtualServer.list_virtual_servers(headers)
    # logger.info(response)

    # Get the status of a virtual server
    # response = VirtualServer.get_virtual_server_status("1x_Quadro_RTX_4000-1692721384", headers)

    # Get the IP address of an active virtual server
    # get_external_ip(name="4x-rtx-a5000-1691038717", headers=headers)

    # Delete a virtual server
    # VirtualServer.delete_virtual_server("1x_RTX_A5000-1692722275", headers)


if __name__ == "__main__":
    if not COMPUTEX_USERNAME or not COMPUTEX_PASSWORD:
        raise Exception("Please set the COMPUTEX_USERNAME and COMPUTEX_PASSWORD environment variables.")

    if not VIRTUAL_SERVER_USERNAME or not VIRTUAL_SERVER_PASSWORD:
        raise Exception("Please set the desired username and password for the virtual server.")
    main()
