# -*- coding: utf-8 -*-

"""Python files.vc API wrapper and command line interface.

This module provides an interface for interacting with the FilesVC API.

It allows users to upload, download, check, and retrieve information
about files. The operations are handled through HTTP requests to the
FilesVC API, and various methods support file metadata retrieval and
progress tracking during upload/download.

@author: Sasivarnasarma
@contact: sasivarnasarma@protonmail.com
@license: MIT License, see LICENSE file

Copyright (C) 2025
"""

import re
import hashlib
from pathlib import Path
from typing import Dict, List, Union, Callable, Optional, Tuple
from requests.exceptions import HTTPError
from requests import get as req_get, post as req_post, delete as req_delete
from requests_toolbelt import MultipartEncoderMonitor

from files_vc.types import FileInfo, FilesVCException
from files_vc.utils import convert_to_datetime


class FilesVC:
    """A class to interact with the FilesVC API, providing methods to upload,
    download, check, and retrieve information about files stored on the FilesVC
    platform. Supports progress tracking for file uploads and downloads.

    Attributes:
        account_id (str): The account ID for the API requests, optional.

    Methods:
        get_file_info(file_hash: str) -> FileInfo:
            Retrieves detailed information about a file by its hash.

        list_files(account_id: str) -> List[FileInfo]:
            Retrieves a list of files for a given account ID.

        check_file(file_path: Union[str, Path], progress: Optional[Callable] = None,
                   progress_args: Optional[Tuple] = ()) -> Optional[FileInfo]:
            Checks the integrity of a file and retrieves its information by hash.

        download_file(file_url: Optional[str] = None, file_hash: Optional[str] = None,
                      save_path: Optional[Union[str, Path]] = None,
                      progress: Optional[Callable] = None,
                      progress_args: Optional[Tuple] = ()) -> Path:
            Downloads a file using either its URL or hash, with optional progress tracking.

        upload_file(file_path: Union[str, Path], account_id: Optional[str] = None,
               progress: Callable[[int, int, Tuple], None] = None,
               progress_args: Optional[Tuple] = ()) -> Tuple[str, FileInfo]:
            Uploads a file to the server, with progress tracking support.
    """

    def __init__(self, account_id: str = None, api_key: str = None):
        """Initialize the files_vc object with account ID, API URL, and
        headers.

        :param account_id: The account ID to be used for API requests,
            optional.
        :type account_id: str
        :param api_key: The API key is used for authentication while uploading.
            This parameter is optional here; however, if it is not provided,
            it must be included when making the `upload_file` request.
            To get an API key, see: https://files.vc/api.
        :type api_key: str
        """
        self.account_id = account_id
        self.api_key = api_key
        self.api_url = "https://api.files.vc"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
            ),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }

    def _make_file_info(self, data: Dict) -> FileInfo:
        """Internal method to create FileInfo object from API response data.

        :param data: Dictionary response from API containing file info.
        :type data: Dict
        :return: FileInfo object with file info.
        :rtype: FileInfo
        :raises FilesVCException: If there is an error processing the
            data.
        """
        try:
            file_info = FileInfo(
                name=data.get("filename", "Unknown"),
                file_hash=data.get("file_hash"),
                size=data.get("file_size"),
                upload_time=(
                    convert_to_datetime(data.get("upload_time"))
                    if data.get("upload_time")
                    else None
                ),
                mime_type=data.get("mime_type", "Unknown"),
                download_count=data.get("download_count", 0),
                expiration_time=(
                    convert_to_datetime(data.get("expiration_time"))
                    if data.get("expiration_time")
                    else None
                ),
                view_url=f"https://files.vc/d/dl?hash={data.get('file_hash')}",
                download_url=data.get("file_url"),
            )
        except ValueError as e:
            raise FilesVCException(f"Error processing data: {e}.") from e

        return file_info

    def get_file_info(
        self, file_hash: Optional[str] = None, file_url: Optional[str] = None
    ) -> FileInfo:
        """Retrieve detailed information about a file from the server.

        Either `file_url` or `file_hash` must be provided, but not both.
        If neither is provided or if both are provided, a `FilesVCException` will be raised.

        :param file_hash: Hash of the file to retrieve info for.
        :type file_hash: Optional[str]
        :param file_url: URL of the file to retrieve info for.
        :type file_url: Optional[str]
        :return: FileInfo object containing detailed file information.
        :rtype: FileInfo
        :raises FilesVCException: If neither `file_url` nor `file_hash` is provided,
            if both are provided or if `file_url` is not a valid URL.
        :raises HTTPError: If an error occurs during the HTTP request.
        """
        if not (file_url or file_hash):
            raise FilesVCException("Error: Either file_url or file_hash is required.")
        if file_url and file_hash:
            raise FilesVCException(
                "Error: Only one of file_url or file_hash can be provided, not both."
            )

        if not file_hash:
            match = re.search(r"\b[a-f0-9]{32}\b", file_url)
            if match:
                file_hash = match.group(0)
            else:
                raise FilesVCException("Error: Unable to extract file hash from URL.")

        url = f"{self.api_url}/api/info?hash={file_hash}"
        response = req_get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return self._make_file_info(data)

    def list_files(self, account_id: Optional[str] = None) -> List[FileInfo]:
        """Retrieve a list of files associated with the current or specified
        account ID.

        :param account_id: Account ID to retrieve files for. If not
            specified, uses the account ID set during object init.
        :type account_id: str
        :return: List of FileInfo objects containing detailed file
            information.
        :rtype: List[FileInfo]
        :raises HTTPError: If an error occurs during the HTTP request.
        :raises FilesVCException: If the account ID is not specified.
        """
        account_id = account_id or self.account_id
        if not account_id:
            raise FilesVCException("Error: Account ID is required.")

        url = f"{self.api_url}/api/account/files?account_id={account_id}"
        response = req_get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        files_data = response.json()

        return [self._make_file_info(file_info) for file_info in files_data["files"]]

    def delete_file(
        self,
        file_hash: Optional[str] = None,
        file_url: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> str:
        """Delete a file by hash or URL.

        Either `file_url` or `file_hash` must be provided, but not both.
        If neither is provided or if both are provided, a `FilesVCException` will be raised.

        :param file_hash: Hash of the file to be deleted.
        :type file_hash: Optional[str]
        :param file_url: URL of the file to be deleted.
        :type file_url: Optional[str]
        :param account_id: Account ID to associate the deletion with.
        :type account_id: Optional[str]
        :return: Success message if the file was deleted.
        :rtype: str
        :raises FilesVCException: If the account ID is not specified,
            if neither `file_url` nor `file_hash` is provided,
            if both are provided, if `file_url` is not a valid URL,
            or If the file is not found.
        :raises HTTPError: If an error occurs during the HTTP request.
        """
        if not (file_url or file_hash):
            raise FilesVCException("Error: Either file_url or file_hash is required.")
        if file_url and file_hash:
            raise FilesVCException(
                "Error: Only one of file_url or file_hash can be provided, not both."
            )

        if not file_hash:
            match = re.search(r"\b[a-f0-9]{32}\b", file_url)
            if match:
                file_hash = match.group(0)
            else:
                raise FilesVCException("Error: Unable to extract file hash from URL.")

        account_id = account_id or self.account_id
        if not account_id:
            raise FilesVCException("Error: Account ID is required.")
        headers = self.headers.copy()
        headers.update({"X-Account-ID": account_id})

        url = f"{self.api_url}/api/file/delete?hash={file_hash}"
        response = req_delete(url, headers=headers, timeout=30)
        if response.status_code == 200:
            response = response.json()
            if response["success"]:
                return response["message"]
            raise FilesVCException(f"Error: {response['message']}")
        if response.status_code == 404:
            raise FilesVCException(
                "Error: The file is not linked to the given Account ID or not found on the server."
            )
        response.raise_for_status()
        return None

    def check_file(
        self,
        file_path: Union[str, Path],
        progress: Optional[Callable[[int, int, Tuple], None]] = None,
        progress_args: Optional[Tuple] = (),
    ) -> Optional[FileInfo]:
        """Check the existence and integrity of a file by computing its hash
        and retrieving its information.

        :param file_path: The path to the file to be checked.
        :type file_path: Union[str, Path]
        :param progress: Optional callback function to report progress.
        :type progress: Optional[Callable[[int, int, Tuple], None]]
        :param progress_args: Additional arguments to pass to the
            progress callback.
        :type progress_args: Tuple
        :return: FileInfo object containing file information if found,
            else None.
        :rtype: Optional[FileInfo]
        :raises FilesVCException: If the file is not found.
        :raises TypeError: If progress is not a callable function.
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        if not file_path.exists():
            raise FilesVCException("Error: File not found locally, check path.")

        if progress and not callable(progress):
            raise TypeError("Error: Progress must be a callable function.")

        total_size = file_path.stat().st_size
        hasher = hashlib.md5()
        bytes_processed = 0

        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(65536), b""):
                hasher.update(chunk)
                bytes_processed += len(chunk)
                if progress:
                    progress(bytes_processed, total_size, *progress_args)

        file_hash = hasher.hexdigest()

        try:
            file_info = self.get_file_info(file_hash=file_hash)
        except HTTPError:
            file_info = None

        return file_info

    def download_file(
        self,
        file_url: Optional[str] = None,
        file_hash: Optional[str] = None,
        save_path: Optional[Union[str, Path]] = None,
        progress: Optional[Callable[[int, int, Tuple], None]] = None,
        progress_args: Optional[Tuple] = (),
    ) -> Path:
        """Download a file based on either a file URL or file hash.

        Either `file_url` or `file_hash` must be provided, but not both.
        If neither is provided or if both are provided, a `FilesVCException` will be raised.

        :param file_url: URL for the file to be downloaded.
        :type file_url: Optional[str]
        :param file_hash: Hash of the file to be downloaded.
        :type file_hash: Optional[str]
        :param save_path: Path to save the downloaded file to.
        :type save_path: Union[str, Path]
        :param progress: Optional callback function to report progress.
        :type progress: Optional[Callable[[int, int, Tuple], None]]
        :param progress_args: Additional arguments to pass to the
            progress callback.
        :type progress_args: Tuple
        :return: Path to the downloaded file.
        :rtype: Path
        :raises FilesVCException: If neither `file_url` nor `file_hash` is provided,
            if both are provided, if `file_url` is not a valid URL, or if the file already exists.
        :raises TypeError: If progress is not a callable function.
        :raises HTTPError: If an error occurs during the HTTP request.
        """
        if not (file_url or file_hash):
            raise FilesVCException("Error: Either file_url or file_hash is required.")
        if file_url and file_hash:
            raise FilesVCException(
                "Error: Only one of file_url or file_hash can be provided, not both."
            )

        if not file_hash:
            match = re.search(r"\b[a-f0-9]{32}\b", file_url)
            if match:
                file_hash = match.group(0)
            else:
                raise FilesVCException("Error: Unable to extract file hash from URL.")

        file_details = self.get_file_info(file_hash=file_hash)
        save_path = save_path or Path.cwd() / "Downloads"
        if not isinstance(save_path, Path):
            save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = save_path / file_details.name

        if file_path.exists():
            raise FilesVCException("Error: File already exists.")

        if progress and not callable(progress):
            raise TypeError("Error: Progress must be a callable function")

        response = req_get(
            file_details.download_url, headers=self.headers, timeout=60 * 2, stream=True
        )
        response.raise_for_status()
        total_length = int(response.headers.get("Content-Length", file_details.size))

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(4096):
                file.write(chunk)
                if progress:
                    progress(file.tell(), total_length, *progress_args)

        return file_path

    def upload_file(
        self,
        file_path: Union[str, Path],
        api_key: Optional[str] = None,
        account_id: Optional[str] = None,
        progress: Callable[[int, int, Tuple], None] = None,
        progress_args: Optional[Tuple] = (),
    ) -> Tuple[str, FileInfo]:
        """Upload a file to the server.

        :param file_path: The path to the file to be uploaded.
        :type file_path: Union[str, Path]
        :param api_key: The API key is used for authentication during
            uploads. If the API key was not provided during the 
            `FilesVC()` request, it must be included here.
            To get an API key, see: https://files.vc/api.
        :type api_key: str
        :param account_id: The account ID to associate the file with.
        :type account_id: str
        :param progress: Optional callback function to report progress.
        :type progress: Callable[[int, int, Tuple], None]
        :param progress_args: Additional arguments to pass to the
            progress callback.
        :type progress_args: Tuple
        :return: Tuple containing a success message and a FileInfo
            object containing file information.
        :rtype: Tuple[str, FileInfo]
        :raises FilesVCException: If the api key is not specified or
            api key is invalid or if the file is not found, empty, or
            exceeds the maximum allowed size.
        :raises TypeError: If progress is not a callable function.
        :raises HTTPError: If an error occurs during the HTTP request.
        """
        account_id = account_id or self.account_id
        api_key = api_key or self.api_key

        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        if not api_key:
            raise FilesVCException("Error: API key is required for uploading files.")

        if not file_path.is_file():
            raise FilesVCException("Error: Not a file")

        if not file_path.exists():
            raise FilesVCException("Error: File not found")

        file_size = file_path.stat().st_size
        if file_size > 10 * 1024 * 1024 * 1024:  # 10GB:
            raise FilesVCException("Error: File size should not exceed 10GB")

        if file_size == 0:
            raise FilesVCException("Error: File is empty")

        if progress and not callable(progress):
            raise TypeError("Error: Progress must be a callable function")

        def callback(monitor: MultipartEncoderMonitor) -> None:
            """Progress callback to update progress during upload.

            :param monitor: The monitor that tracks the upload progress.
            :type monitor: MultipartEncoderMonitor
            :return: None
            :rtype: None
            """
            if progress:
                progress(monitor.bytes_read, monitor.len, *progress_args)

        with open(file_path, mode="rb") as file:
            fields = {"file": (file_path.name, file, "application/octet-stream")}
            encoder_monitor = MultipartEncoderMonitor.from_fields(
                fields, callback=callback
            )

            headers = self.headers.copy()
            if account_id:
                headers.update({"X-Account-ID": account_id})
            headers.update({"X-API-Key": api_key})
            headers.update({"Content-Type": encoder_monitor.content_type})

            response = req_post(
                f"{self.api_url}/upload",
                data=encoder_monitor,
                headers=headers,
                timeout=60 * 5,
            )
        if response.status_code == 403:
            raise FilesVCException("Error: Invalid API key")
        response.raise_for_status()
        res_json = response.json()
        message = res_json.get("message")
        file_info = self.get_file_info(file_hash=res_json["debug_info"]["hash"])

        return message, file_info
