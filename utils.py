import sys
import plistlib
from pathlib import Path
from typing import Optional
from pefile import PE, DIRECTORY_ENTRY
import requests
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_blocks_to_run(base_url: str, worker_id: str) -> list[str] | dict[str, str]:
    """
    Sends a GET request to retrieve the list of blocks that are yet to be run by the worker.

    Args:
        base_url (str): The base URL of the API server (e.g., "https://your-api-server.com").
        worker_id (str): The unique identifier for the worker whose blocks are being fetched.

    Returns:
        list: A list of blocks that the worker has yet to run. If an error occurs, a dictionary containing the error code and details is returned.

    Example:
        blocks_to_run = get_blocks_to_run("https://api.example.com", "worker_123")
        logging.info(blocks_to_run)
    """
    # Define the GET request URL
    url = f"{base_url}/taskcontrol"

    # Define the request parameters (query string)
    params = {
        'worker_id': worker_id
    }

    # Send the GET request
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for non-2xx status codes
        # Success: return the blocks to run
        logging.info(
            f"Blocks to run: {response.json().get('blocks_to_run', [])}")
        return response.json().get('blocks_to_run', [])
    except requests.exceptions.HTTPError as http_error:
        logging.error(f"HTTP Error: {http_error}")
    except requests.exceptions.ConnectionError as error_connecting:
        logging.error(f"Error Connecting: {error_connecting}")
    except requests.exceptions.Timeout as timeout_error:
        logging.error(f"Timeout Error: {timeout_error}")
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")
    return {"error": f"Request failed"}


def upload_block(base_url: str, worker_id: str, block_name: str, checksum: str, file_path: str) -> None:
    """
    Sends a POST request to upload a completed block along with its checksum and the associated zipped file.

    Args:
        base_url (str): The base URL of the API server (e.g., "https://your-api-server.com").
        worker_id (str): The unique identifier for the worker who is uploading the block.
        block_name (str): The name of the block being uploaded, typically in the format "taskname_runnumber".
        checksum (str): The 128-character alphanumeric checksum representing the zipped file contents.
        file_path (str): The path to the zipped file that is being uploaded for the block.

    Behavior:
        - Sends the `worker_id`, `block_name`, and `checksum` in the form data.
        - Uploads the zipped file associated with the block in the `files` parameter.
        - Handles successful upload with a status of 200.
        - Handles checksum mismatch with a status of 409, indicating a conflict due to checksum mismatch.

    Example:
        upload_block("https://api.example.com", "worker_123", "task_1", "checksum_string", "/path/to/file.zip")

    """
    # Define the POST request URL
    url = f"{base_url}/taskcontrol"

    # Define the POST request payload
    data = {
        'worker_id': worker_id,
        'block_name': block_name,
        'checksum': checksum
    }

    # Define the files to upload (file should be a zip file for the block)
    files = {
        # Opening the file in binary mode for upload
        'file': open(file_path, 'rb')
    }

    # Send the POST request with form data and file
    try:
        response = requests.post(url, data=data, files=files)
        response.raise_for_status()  # Raise an error for non-2xx status codes
        if response.status_code == 200:
            logging.info("Upload successful!")
        elif response.status_code == 409:
            logging.warning("Checksum mismatch: checksums don't match")
            logging.warning(response.json().get("error", "Unknown error"))
    except requests.exceptions.HTTPError as http_error:
        logging.error(f"HTTP Error: {http_error}")
    except requests.exceptions.ConnectionError as connection_error:
        logging.error(f"Error Connecting: {connection_error}")
    except requests.exceptions.Timeout as timeout_error:
        logging.error(f"Timeout Error: {timeout_error}")
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")
    finally:
        # Close the file to release resources
        files['file'].close()


class NotInAppBundleError(Exception):
    """Custom exception to be raised when executable is not in a macOS .app bundle."""
    pass


def read_app_worker_id() -> Optional[str]:
    """
    Reads the 'WorkerID' from the Info.plist of the currently running .app bundle,
    handling both cases where the .app is launched or the executable is run directly from Contents/MacOS.

    Raises:
        NotInAppBundleError: If the executable is not part of a macOS .app bundle.
        FileNotFoundError: If the Info.plist file is not found in the .app bundle.


    Returns:
        Optional[str]: The value of 'WorkerID' from Info.plist, if found. Returns None if not found.
    """
    exec_path: Path = Path(sys.executable).resolve()

    # If running from Contents/MacOS, go up two directories to get to the .app root
    if exec_path.parent.name == 'MacOS' and exec_path.parents[1].name == 'Contents':
        # Go two levels up (from MacOS to .app root)
        app_bundle_path = exec_path.parents[2]
    else:
        # If the executable is not within a macOS .app bundle, raise an exception
        raise NotInAppBundleError(
            "Executable is not inside a macOS .app bundle.")

    # Build the path to Info.plist
    plist_path: Path = app_bundle_path / 'Contents' / 'Info.plist'

    if not plist_path.exists():
        raise FileNotFoundError(f"Info.plist not found at {plist_path}")

    try:
        with plist_path.open('rb') as plist_file:
            plist_data: dict = plistlib.load(plist_file)
        return plist_data.get('WorkerID')
    except plistlib.InvalidFileException:
        print(f"Error: Invalid plist file at {plist_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {plist_path}: {e}")
        return None


def read_exe_worker_id() -> Optional[str]:
    """
    Reads the 'WorkerID' from the version info resource of the currently running .exe file on Windows.

    Returns:
        Optional[str]: The value of 'WorkerID' from the version info resource if found. Returns None if not found.
    """
    exe_file_path: str = sys.executable
    try:
        pe = PE(exe_file_path, fast_load=True)
        pe.parse_data_directories(
            directories=[DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])

        if hasattr(pe, 'FileInfo'):
            for file_info in pe.FileInfo:
                for info in file_info:
                    if info.name == 'StringFileInfo':
                        version_info_dict: dict[bytes,
                                                bytes] = info.StringTable[0].entries
                        worker_id_bytes: Optional[bytes] = version_info_dict.get(
                            b'WorkerID')

                        if worker_id_bytes:
                            return worker_id_bytes.decode('utf-8')
    except Exception as e:
        print(
            f"An error occurred while reading the executable version info: {e}")

    return None
