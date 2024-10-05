import sys
import plistlib
from pathlib import Path
from typing import Optional
from pefile import PE, DIRECTORY_ENTRY


class NotInAppBundleError(Exception):
    """Custom exception to be raised when executable is not in a macOS .app bundle."""
    pass


def read_app_subject_id() -> Optional[str]:
    """
    Reads the 'SubjectID' from the Info.plist of the currently running .app bundle,
    handling both cases where the .app is launched or the executable is run directly from Contents/MacOS.

    Raises:
        NotInAppBundleError: If the executable is not part of a macOS .app bundle.
        FileNotFoundError: If the Info.plist file is not found in the .app bundle.


    Returns:
        Optional[str]: The value of 'SubjectID' from Info.plist, if found. Returns None if not found.
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
        return plist_data.get('SubjectID')
    except plistlib.InvalidFileException:
        print(f"Error: Invalid plist file at {plist_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {plist_path}: {e}")
        return None


def read_exe_subject_id() -> Optional[str]:
    """
    Reads the 'SubjectID' from the version info resource of the currently running .exe file on Windows.

    Returns:
        Optional[str]: The value of 'SubjectID' from the version info resource if found. Returns None if not found.
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
                        subject_id_bytes: Optional[bytes] = version_info_dict.get(
                            b'SubjectID')

                        if subject_id_bytes:
                            return subject_id_bytes.decode('utf-8')
    except Exception as e:
        print(
            f"An error occurred while reading the executable version info: {e}")

    return None
