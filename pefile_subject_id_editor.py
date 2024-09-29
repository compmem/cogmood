import logging
import os
from typing import Optional
from pefile import PE, DIRECTORY_ENTRY
from pathlib import Path


def edit_exe_subject_id(exe_file_path: str, new_subject_id: str, output_file_path: Optional[str] = None) -> None:
    """
    Modifies the 'SubjectID' field in the version information of an executable.

    Args:
        exe_file_path (str): Path to the executable whose 'SubjectID' will be modified.
        new_subject_id (str): New 'SubjectID' value to replace the existing one. 
                              **Must** be less than or equal to the length of the current 'SubjectID' for a successful update.
        output_file_path (str): **Optional**. Path where the modified executable will be saved. 
                                If not provided, the original executable will be overwritten.

    Raises:
        FileNotFoundError: If the specified executable does not exist.
        ValueError: If the PE file cannot be loaded or parsed.
    """

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    if not os.path.exists(exe_file_path):
        raise FileNotFoundError(f"The file {exe_file_path} does not exist.")

    output_file_path = Path(output_file_path or exe_file_path)

    try:
        pe: PE = PE(exe_file_path, fast_load=True)
        pe.parse_data_directories(
            directories=[DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']])
    except Exception as e:
        raise ValueError(f"Failed to load or parse the PE file: {e}")

    # Access the SubjectID and update it if found
    if hasattr(pe, 'FileInfo'):
        for file_info in pe.FileInfo:
            for info in file_info:
                if info.name == 'StringFileInfo':
                    version_info_dict: dict = info.StringTable[0].entries
                    subject_id_bytes: bytes = version_info_dict.get(
                        b'SubjectID', None)

                    if subject_id_bytes:
                        logging.info(
                            f"Found SubjectID: {subject_id_bytes.decode('utf-8')}")

                        # Calculate the original size in bytes and the new value size
                        original_size: int = len(subject_id_bytes)
                        new_subject_id_bytes: bytes = new_subject_id.encode(
                            'utf-8')
                        new_size: int = len(new_subject_id_bytes)

                        if new_size <= original_size:
                            # Create the new value padded with null bytes up to the original size
                            padded_new_subject_id: bytes = new_subject_id_bytes + \
                                b'\x00' * (original_size - new_size)

                            # Update the value with the padded version
                            version_info_dict[b"SubjectID"] = padded_new_subject_id

                            # Write the updated attribute to the output file
                            pe.write(output_file_path)
                            logging.info(
                                f"Successfully updated SubjectID to {new_subject_id}")
                        else:
                            logging.error(
                                f"Error: New value '{new_subject_id}' is larger than the existing space of {original_size} bytes.")
                        return

    logging.error(f"Error: SubjectID not found in {exe_file_path}")


if __name__ == "__main__":
    edit_exe_subject_id(
        exe_file_path="package\\dist\\test.exe",
        new_subject_id="023456789",
        output_file_path="output.exe"
    )
