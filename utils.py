import os
import sys
import plistlib
import zipfile
import requests
import logging
from config import API_BASE_URL
from hashlib import blake2b
from io import BytesIO
from pathlib import Path
from typing import Optional
from pefile import PE, DIRECTORY_ENTRY


# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_blocks_to_run(worker_id: str) -> list[str] | dict[str, str]:
    """
    Sends a GET request to retrieve the list of blocks that are yet to be run by the worker.

    Args:
        base_url (str): The base URL of the API server (e.g., "https://your-api-server.com").
        worker_id (str): The unique identifier for the worker whose blocks are being fetched.

    Returns:
        list: A list of blocks that the worker has yet to run. If an error occurs, a dictionary containing the error code and details is returned.

    Example:
        blocks_to_run = get_blocks_to_run("https://api.example.com", "worker_123")
    """
    # Define the GET request URL
    url = f"{API_BASE_URL}/taskcontrol"

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
        return {"error": "HTTP Error"}
    except requests.exceptions.ConnectionError as error_connecting:
        logging.error(f"Error Connecting: {error_connecting}")
        return {"error": "Error Connecting"}
    except requests.exceptions.Timeout as timeout_error:
        logging.error(f"Timeout Error: {timeout_error}")
        return {"error": "Timeout Error"}
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")
        return {"error": "Unspecified Error"}


def hash_file(file_obj):
    """
    Computes the blake2b hash of a file-like object.

    Args:
        file_obj: File-like object opened in binary mode.

    Returns:
        str: The hexadecimal representation of the hash.
    """
    hash_blake = blake2b()
    file_obj.seek(0)  # Reset file pointer to the start
    for chunk in iter(lambda: file_obj.read(4096), b""):
        hash_blake.update(chunk)
    return hash_blake.hexdigest()


def upload_block(worker_id: str, block_name: str, data_directory: str, slog_file_name: str) -> dict[str, str]:
    """
    Sends a POST request to upload a completed block along with its checksum and the associated zipped file.
    Uses the config.API_BASE_URL to build the URL.

    Args:
        worker_id (str): The unique identifier for the worker who is uploading the block.
        block_name (str): The name of the block being uploaded, typically in the format "taskname_runnumber".
        data_directory (str): The directory where the slog file is located.
        slog_file_name (str): The name of the slog file.

    Behavior:
        - Zips the slog file.
        - Computes the checksum of the zipped file.
        - Sends the `worker_id`, `block_name`, and `checksum` in the form data.
        - Uploads the zipped file associated with the block in the `files` parameter.

    Returns:
        dict: A dictionary containing a 'success' key with a message if the upload is successful,
              or an 'error' key with the type of error encountered.
              Example return values:
              {'success': 'Data upload successful.'} on successful upload.
              {'error': 'Checksum mismatch'} if the checksum does not match.
              {'error': 'Connection error'} if there is a connection issue.
    """
    url = f"{API_BASE_URL}/taskcontrol"

    slog_file_path = os.path.join(data_directory, slog_file_name)
    if not os.path.isfile(slog_file_path):
        logging.warning(f"File '{slog_file_name}' does not exist at '{slog_file_path}'.")
        return {"error": "Log file not found"}

    logging.info(f"SLOG File Found: File '{slog_file_name}' exists at '{slog_file_path}'.")

    # Create a zip archive in memory
    zip_buffer = BytesIO()
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(slog_file_path, slog_file_name)

        zip_buffer.seek(0)  # Reset buffer to the start
        checksum = hash_file(zip_buffer)
        zip_buffer.seek(0)  # Reset the buffer to the start again for upload

        params = {'worker_id': worker_id}
        data = {'block_name': block_name, 'checksum': checksum}
        files = {'file': (f'{block_name}.zip', zip_buffer, 'application/zip')}

        response = requests.post(url, params=params, data=data, files=files)
        logging.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            logging.info("Upload successful!")
            return {'success': 'Data upload successful.'}  # Indicating success
        elif response.status_code == 400:
            error_message = response.json().get("error", "Unknown error")
            logging.warning(f"Bad Request: {error_message}")
            return {"error": error_message}
        elif response.status_code == 409:
            error_message = response.json().get("error", "Unknown error")
            logging.warning("Checksum mismatch: checksums don't match")
            logging.warning(f"Error: {error_message}")
            return {"error": "Checksum mismatch"}
        else:
            logging.error(f"Unexpected response: {response.status_code} - {response.text}")
            return {"error": f"Unexpected response: {response.status_code}"}

    except requests.exceptions.ConnectionError as connection_error:
        logging.error(f"Error Connecting: {connection_error}")
        return {"error": "Connection error"}
    except requests.exceptions.Timeout as timeout_error:
        logging.error(f"Timeout Error: {timeout_error}")
        return {"error": "Timeout error"}
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")
        return {"error": "Request error"}
    finally:
        zip_buffer.close()


def read_app_worker_id() -> Optional[str]:
    """
    Reads the 'WorkerID' from the Info.plist of the currently running .app bundle,
    handling both cases where the .app is launched or the executable is run directly from Contents/MacOS.

    Logs warnings instead of raising exceptions in case of errors.

    Returns:
        Optional[str]: The value of 'WorkerID' from Info.plist, if found. Returns None if not found.
    """
    exec_path: Path = Path(sys.executable).resolve()

    # If running from Contents/MacOS, go up two directories to get to the .app root
    if exec_path.parent.name == 'MacOS' and exec_path.parents[1].name == 'Contents':
        # Go two levels up (from MacOS to .app root)
        app_bundle_path = exec_path.parents[2]
    else:
        # Log a warning if the executable is not within a macOS .app bundle
        logging.warning("Executable is not inside a macOS .app bundle.")
        return None

    # Build the path to Info.plist
    plist_path: Path = app_bundle_path / 'Contents' / 'Info.plist'

    if not plist_path.exists():
        logging.warning(f"Info.plist not found at {plist_path}")
        return None

    try:
        with plist_path.open('rb') as plist_file:
            plist_data: dict = plistlib.load(plist_file)
        worker_id = plist_data.get('WorkerID')
        if worker_id:
            logging.info(f"WorkerID found: {worker_id}")
        else:
            logging.warning("WorkerID not found in Info.plist")
        return worker_id
    except plistlib.InvalidFileException:
        logging.error(f"Invalid plist file at {plist_path}")
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while reading {plist_path}: {e}")
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
                            worker_id = worker_id_bytes.decode('utf-8')
                            logging.info(f"WorkerID found: {worker_id}")
                            return worker_id
                        else:
                            logging.warning(
                                "WorkerID not found in executable version info")
    except Exception as e:
        logging.error(
            f"An error occurred while reading the executable version info: {e}")

    return None


if __name__ == "__main__":
    upload_block(worker_id='123456',
                 block_name='flkr_1',
                 data_directory='SUPREMEMOOD/1/20241016_185342/',
                 slog_file_name='log_bart_1.slog')