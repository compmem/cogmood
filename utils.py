import sys
import plistlib
import zipfile
import requests
import logging
import time
from config import API_BASE_URL, RUNNING_FROM_EXECUTABLE, CURRENT_OS, VERIFY, WORKER_ID_SOURCE,\
    UPLOAD_EXTRA_FILES, EXPECTED_NUMBER_OF_BLOCKS
from hashlib import blake2b
from io import BytesIO
from pathlib import Path
from typing import Optional
from pefile import PE, DIRECTORY_ENTRY


# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_blocks_to_run(worker_id: str, code: str | None = None) -> list[str] | dict[str, str]:
    """
    Sends a GET request to retrieve the list of blocks that are yet to be run by the worker.

    Args:
        worker_id (str): The unique identifier for the worker whose blocks are being fetched.
        code (str): Optional verifcation code if worker_id_source is user

    Returns:
        dict: A dictionary with 'status' as success or error, and 'content' containing either the blocks list or an error message.
    """
    if API_BASE_URL == 'NOSERVER':
        logging.info('API_BASE_URL set to NOSERVER, faking server responses')
        tasks = ["rdm", "flkr", "bart", "cab"]
        reformatted_tasks = []
        for bn in [0, 1]:
            for tt in tasks:
                reformatted_tasks.append({'task_name':tt, 'block_number': bn})
        logging.info(f'Reformatted task list: {reformatted_tasks}')
        return {'status': 'success', 'content': reformatted_tasks}
    url = f'{API_BASE_URL}/taskcontrol'
    if WORKER_ID_SOURCE == 'EXECUTABLE':
        params = {'worker_id': worker_id}
    elif WORKER_ID_SOURCE == 'USER':
        params = {'worker_id': worker_id, 'code':code}

    try:
        response = requests.get(url, params=params, verify=VERIFY)
        response.raise_for_status()  # Raise an error for non-2xx status codes
        tasks = response.json().get('blocks_to_run', [])
        logging.info(f'Tasks to run: {tasks}')
        
        # Format tasks from ['flkr_0] into [{'task_name': 'flkr', 'block_number': 0}]
        reformatted_tasks = [{'task_name': task.split('_')[0], 'block_number': int(task.split('_')[1])}
                             for task in tasks]
        logging.info(f'Reformatted task list: {reformatted_tasks}')
        return {'status': 'success', 'content': reformatted_tasks}
    
    except requests.exceptions.HTTPError as http_error:
        error_message = response.json().get('error', 'HTTP Error')
        logging.error(f'HTTP Error: {http_error} - {error_message}')
        return {'status': 'error', 'content': error_message}
    
    except requests.exceptions.ConnectionError as error_connecting:
        logging.error(f'Error Connecting: {error_connecting}')
        return {'status': 'error', 'content': 'Error Connecting'}
    
    except requests.exceptions.Timeout as timeout_error:
        logging.error(f'Timeout Error: {timeout_error}')
        return {'status': 'error', 'content': 'Timeout Error'}
    
    except requests.exceptions.RequestException as error:
        logging.error(f'An error occurred: {error}')
        error_message = response.json().get('error', 'Unspecified Error')
        return {'status': 'error', 'content': error_message}


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

def upload_happy(worker_id: str, block_name: str, data_directory: str, code: str | None = None) -> dict[str, str]:
    """
    Function to upload all of the non-empty happy blocks found

    Args:
        worker_id (str): The unique identifier for the worker who is uploading the block.
        block_name (str): The name of the block being uploaded, typically in the format "taskname_runnumber".
        data_directory (str): The directory where the slog file is located.
        code (str): Optional verifcation code if worker_id_source is user.

    Behavior:
        - Finds all of the slog files
        - Zips them up
        - Sends the `worker_id`, `block_name`, and `checksum` in the form data.
        - Uploads the zipped file associated with the block in the `files` parameter.

     Returns:
        dict: A dictionary with 'status' ('success' or 'error') and 'content' (message or error details).
    """
    if API_BASE_URL == 'NOSERVER':
        logging.info('API_BASE_URL set to NOSERVER, skipping upload')
        return {"status": "success", "content": "Data upload skipped."}
    url = f"{API_BASE_URL}/taskcontrol"

    slog_files = sorted(Path(data_directory).glob('log_happy*.slog'))
    zip_buffer = BytesIO()
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for slog_file_path in slog_files:
                zip_file.write(slog_file_path, slog_file_path.parts[-1])

        zip_buffer.seek(0)
        checksum = hash_file(zip_buffer)
        zip_buffer.seek(0)

        current_time_ms = int(time.time() * 1000)
        zip_file_name_with_timestamp = f'{block_name}_{current_time_ms}.zip'

        if WORKER_ID_SOURCE == 'EXECUTABLE':
            params = {'worker_id': worker_id}
        elif WORKER_ID_SOURCE == 'USER':
            params = {'worker_id': worker_id, 'code': code}
        data = {'block_name': block_name, 'checksum': checksum}
        files = {'file': (zip_file_name_with_timestamp, zip_buffer, 'application/zip')}

        response = requests.post(url, params=params, data=data, files=files, verify=VERIFY)
        logging.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            logging.info("Upload successful!")
            return {"status": "success", "content": "Data upload successful."}
        elif response.status_code == 400:
            error_message = response.json().get("error", "Unknown error")
            logging.warning(f"Bad Request: {error_message}")
            return {"status": "error", "content": error_message}
        elif response.status_code == 409:
            logging.warning("Checksum mismatch: checksums don't match")
            return {"status": "error", "content": "Checksum mismatch"}
        else:
            logging.error(f"Unexpected response: {response.status_code} - {response.text}")
            return {"status": "error", "content": f"Unexpected response: {response.status_code}"}

    except requests.exceptions.ConnectionError as connection_error:
        logging.error(f"Error Connecting: {connection_error}")
        return {"status": "error", "content": "Connection error"}
    except requests.exceptions.Timeout as timeout_error:
        logging.error(f"Timeout Error: {timeout_error}")
        return {"status": "error", "content": "Timeout error"}
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")
        return {"status": "error", "content": "Request error"}
    finally:
        zip_buffer.close()


def upload_block(worker_id: str, block_name: str, data_directory: str, slog_file_name: str, code: str | None = None) -> dict[str, str]:
    """
    Sends a POST request to upload a completed block along with its checksum and the associated zipped file.
    Uses the config.API_BASE_URL to build the URL.

    Args:
        worker_id (str): The unique identifier for the worker who is uploading the block.
        block_name (str): The name of the block being uploaded, typically in the format "taskname_runnumber".
        data_directory (str): The directory where the slog file is located.
        slog_file_name (str): The name of the slog file.
        code (str): Optional verifcation code if worker_id_source is user.

    Behavior:
        - Zips the slog file.
        - Computes the checksum of the zipped file.
        - Sends the `worker_id`, `block_name`, and `checksum` in the form data.
        - Uploads the zipped file associated with the block in the `files` parameter.

     Returns:
        dict: A dictionary with 'status' ('success' or 'error') and 'content' (message or error details).
    """
    if API_BASE_URL == 'NOSERVER':
        logging.info('API_BASE_URL set to NOSERVER, skipping upload')
        return {"status": "success", "content": "Data upload skipped."}

    url = f"{API_BASE_URL}/taskcontrol"
    slog_file_path = Path(data_directory) / slog_file_name
    
    if not slog_file_path.is_file():
        logging.warning(f"File '{slog_file_name}' does not exist at '{slog_file_path}'.")
        return {"status": "error", "content": "Log file not found"}
    
    logging.info(f"SLOG File Found: File '{slog_file_name}' exists at '{slog_file_path}'.")
    task_name = block_name.split('_')[0]
    extra_files = UPLOAD_EXTRA_FILES[task_name]
    zip_buffer = BytesIO()
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(slog_file_path, slog_file_name)
            for extra_file, ef_isdir, extra_file_name in extra_files:
                if ef_isdir:
                    efd = Path(data_directory) / extra_file
                    if not efd.exists():
                        return {"status": "error", "content": f"{extra_file} not found"}
                    for efp in efd.glob('*'):
                        logging.info(f"Extra File Found: File '{efp.parts[-1]}' exists at '{efp}'.")
                        zip_file.write(efp, Path(extra_file_name)/efp.parts[-1])
                else:
                    efp = Path(data_directory) / extra_file
                    if not efp.exists():
                        return {"status": "error", "content": f"{extra_file} not found"}
                    logging.info(f"Extra File Found: File '{efp.parts[-1]}' exists at '{efp}'.")
                    zip_file.write(efp, extra_file_name)

        zip_buffer.seek(0)
        checksum = hash_file(zip_buffer)
        zip_buffer.seek(0)
        namelist = zipfile.ZipFile(zip_buffer).namelist()
        zip_buffer.seek(0)
        logging.info(f"Created zipfile has the following contents: {namelist}")
        current_time_ms = int(time.time() * 1000)
        zip_file_name_with_timestamp = f'{block_name}_{current_time_ms}.zip'

        if WORKER_ID_SOURCE == 'EXECUTABLE':
            params = {'worker_id': worker_id}
        elif WORKER_ID_SOURCE == 'USER':
            params = {'worker_id': worker_id, 'code': code}
        data = {'block_name': block_name, 'checksum': checksum}
        files = {'file': (zip_file_name_with_timestamp, zip_buffer, 'application/zip')}

        response = requests.post(url, params=params, data=data, files=files, verify=VERIFY)
        logging.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            logging.info("Upload successful!")
            return {"status": "success", "content": "Data upload successful."}
        elif response.status_code == 400:
            error_message = response.json().get("error", "Unknown error")
            logging.warning(f"Bad Request: {error_message}")
            return {"status": "error", "content": error_message}
        elif response.status_code == 409:
            logging.warning("Checksum mismatch: checksums don't match")
            return {"status": "error", "content": "Checksum mismatch"}
        else:
            logging.error(f"Unexpected response: {response.status_code} - {response.text}")
            return {"status": "error", "content": f"Unexpected response: {response.status_code}"}
    
    except requests.exceptions.ConnectionError as connection_error:
        logging.error(f"Error Connecting: {connection_error}")
        return {"status": "error", "content": "Connection error"}
    except requests.exceptions.Timeout as timeout_error:
        logging.error(f"Timeout Error: {timeout_error}")
        return {"status": "error", "content": "Timeout error"}
    except requests.exceptions.RequestException as error:
        logging.error(f"An error occurred: {error}")
        return {"status": "error", "content": "Request error"}
    finally:
        zip_buffer.close()


def retrieve_worker_id() -> dict[str, str]:
    """
    Retrieves the worker ID based on the current OS and executable context.
    
    Returns:
        dict: A dictionary with 'status' and 'content' containing the worker ID or error message.
    """
    if RUNNING_FROM_EXECUTABLE:

        # Select appropriate worker ID retrieval function based on OS
        os_worker_id_function = {
            'Windows': _read_exe_worker_id,
            'Darwin': _read_app_worker_id
        }.get(CURRENT_OS, lambda: {'status': 'error', 'content': 'Unsupported OS'})

        return os_worker_id_function()

    return {'status': 'error', 'content': 'Not running from an executable'}


def _read_app_worker_id() -> dict[str, str]:
    """
    Reads the 'WorkerID' from the Info.plist of the currently running .app bundle.

    Returns:
        dict: A dictionary containing 'status' and 'content' (either the 'WorkerID' or an error message).
    """
    exec_path: Path = Path(sys.executable).resolve()

    if exec_path.parent.name == 'MacOS' and exec_path.parents[1].name == 'Contents':
        app_bundle_path = exec_path.parents[2]
    else:
        logging.warning("Executable is not inside a macOS .app bundle.")
        return {"status": "error", "content": "Executable is not inside a macOS .app bundle"}

    plist_path: Path = app_bundle_path / 'Contents' / 'Info.plist'

    if not plist_path.exists():
        logging.warning(f"Info.plist not found at {plist_path}")
        return {"status": "error", "content": "Info.plist not found"}

    try:
        with plist_path.open('rb') as plist_file:
            plist_data: dict = plistlib.load(plist_file)
        worker_id = plist_data.get('WorkerID')
        if worker_id:
            logging.info(f"WorkerID found: {worker_id}")
            return {"status": "success", "content": worker_id}
        else:
            logging.warning("WorkerID not found in Info.plist")
            return {"status": "error", "content": "WorkerID not found in Info.plist"}
    except plistlib.InvalidFileException:
        logging.error(f"Invalid plist file at {plist_path}")
        return {"status": "error", "content": "Invalid plist file"}
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading {plist_path}: {e}")
        return {"status": "error", "content": str(e)}


def _read_exe_worker_id() -> dict[str, str]:
    """
    Reads the 'WorkerID' from the version info resource of the currently running .exe file on Windows.

    Returns:
        dict: A dictionary containing 'status' and 'content' (either the 'WorkerID' or an error message).
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
                        version_info_dict: dict[bytes, bytes] = info.StringTable[0].entries
                        worker_id_bytes: Optional[bytes] = version_info_dict.get(b'WorkerID')

                        if worker_id_bytes:
                            worker_id = worker_id_bytes.decode('utf-8')
                            logging.info(f"WorkerID found: {worker_id}")
                            return {"status": "success", "content": worker_id}
                        else:
                            logging.warning("WorkerID not found in executable version info")
                            return {"status": "error", "content": "WorkerID not found"}
    except Exception as e:
        logging.error(f"An error occurred while reading the executable version info: {e}")
        return {"status": "error", "content": str(e)}


def sid_evenness(sid, hash_input=False):
    # make sure the input is a string
    sid = str(sid)
    if hash_input:
        sid = blake2b(sid.encode(), digest_size=4).hexdigest()
    # initialize val so we can later catch if it never got set
    val = None
    # loop through the SID backwards looking for something that
    # ord will return a value on
    # I'm using a naked except because I don't care how ord fails
    for char in sid[::-1]:
        try:
            val = ord(char)
            break
        except:
            continue
    # if for some reason ord works on nothing in sid
    # then just use the length
    # if all SIDs are the same length, this'll be a problem
    # but I really don't expect to get this far
    # and we'll keep an eye on use of this in the data
    if val is None:
        val = len(sid)

    if val % 2 == 0:
        return True
    else:
        return False


def make_n_block_message(blocklist):
    n = len(blocklist)
    if n == EXPECTED_NUMBER_OF_BLOCKS:
        message = "No blocks have been completed and uploaded. You will start from the first of " \
                  f" {EXPECTED_NUMBER_OF_BLOCKS} total blocks."\
                  f" Press any key to continue."
    else:
        message = f"You have completed and successfully uploaded {EXPECTED_NUMBER_OF_BLOCKS - n} out of " \
                  f"{EXPECTED_NUMBER_OF_BLOCKS} total blocks. You will start from " \
                  f"block {EXPECTED_NUMBER_OF_BLOCKS - n + 1}.\n\n Press any key to continue."
    return message


if __name__ == "__main__":
    upload_block(worker_id='123456',
                 block_name='flkr_1',
                 data_directory='SUPREMEMOOD/1/20241016_185342/',
                 slog_file_name='log_bart_1.slog')
