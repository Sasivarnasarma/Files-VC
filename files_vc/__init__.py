# -*- coding: utf-8 -*-

"""Python files.vc API wrapper and command line interface.

@author: Sasivarnasarma
@contact: sasivarnasarma@protonmail.com
@license: MIT License, see LICENSE file

Copyright (C) 2025
"""

__title__ = "FilesVC"
__author__ = "Sasivarnasarma"
__author_email__ = "sasivarnasarma@protonmail"
__license__ = "MIT"
__version__ = "1.0.3"
__all__ = (
    "__version__",
    "FilesVC",
    "FileInfo",
    "FilesVCException",
    "HTTPError",
)
from requests.exceptions import HTTPError

from ._main import FilesVC
from .types import FileInfo, FilesVCException
