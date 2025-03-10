# -*- coding: utf-8 -*-

"""Python files.vc API wrapper and command line interface.

Module to handle file information and custom exception for the FilesVC API.

This module defines the `FileInfo` data class to store metadata about files
and the `FilesVCException` custom exception class for handling errors related
to the FilesVC API interactions.

@author: Sasivarnasarma
@contact: sasivarnasarma@protonmail.com
@license: MIT License, see LICENSE file

Copyright (C) 2025
"""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class FileInfo:
    """A class to represent file information.

    Attributes:
        name (str): The name of the file.
        file_hash (str): A unique hash representing the file.
        size (int): The size of the file in bytes.
        upload_time (datetime): The timestamp when the file was uploaded.
        mime_type (str): The MIME type of the file (e.g., 'image/jpeg').
        download_count (int): The number of times the file has been downloaded.
        expiration_time (datetime): The expiration date of the file, if applicable.
        view_url (str): A URL to view the file.
        download_url (str): A URL to download the file.
    """

    name: str
    file_hash: str
    size: int
    upload_time: datetime
    mime_type: str
    download_count: int
    expiration_time: datetime
    view_url: str
    download_url: str


class FilesVCException(Exception):
    """Custom exception for handling errors related to FilesVC API operations.

    This exception is raised when there is an error with file handling,
    such as file not found or other API-specific issues.

    Attributes:
        message (str): The error message describing the issue.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
