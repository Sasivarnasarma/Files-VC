# -*- coding: utf-8 -*-

"""Python files.vc API wrapper and command line interface.

@author: Sasivarnasarma
@contact: sasivarnasarma@protonmail.com
@license: MIT License, see LICENSE file

Copyright (C) 2025
"""

import re
import sys
import time
import argparse
from tabulate import tabulate

from files_vc import __version__, FilesVC, FileInfo, FilesVCException, HTTPError
from files_vc.utils import get_readable_file_size, display_progress, reset_line


def create_table(file_info: FileInfo, tablefmt: str) -> str:
    """Create a table from a FileInfo object."""
    table_data = [
        ["Name", file_info.name],
        ["File Hash", file_info.file_hash],
        ["Size", get_readable_file_size(file_info.size)],
        ["Upload Time", file_info.upload_time.strftime("%Y-%m-%d %H:%M:%S") + " UTC"],
        ["MIME Type", file_info.mime_type],
        ["Download Count", file_info.download_count],
        ["View URL", file_info.view_url],
        ["Download URL", file_info.download_url],
    ]
    if file_info.expiration_time:
        table_data.insert(4, ["Expiration Time", file_info.expiration_time])
    return tabulate(table_data, tablefmt=tablefmt)


def main():
    """Command line interface for Files.VC.

    This function parses the command line arguments and handles the
    following commands:

    - info: Retrieves detailed information about a file by its hash.
    - list: Retrieves a list of files for a given account ID.
    - check: Checks the integrity of a file and retrieves its information by hash.
    - upload/ul: Uploads a file to the server, with progress tracking support.
    - download/dl: Downloads a file using either its URL or hash, with optional
        progress tracking.

    :return: None
    :rtype: None
    """
    parser = argparse.ArgumentParser(
        prog="files-vc", description="Files.VC Command Line Tool"
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-t",
        "--tablefmt",
        type=str,
        default="plain",
        help="Tabulate Table format for display File info (default: plain)",
        metavar="",
    )

    subparsers = parser.add_subparsers(
        title="Commands",
        description="Available commands",
        metavar="[info, list, check, upload/ul, download/dl]",
        dest="command",
        required=True,
    )

    info_parser = subparsers.add_parser("info", help="Get file info from the server")
    info_parser.add_argument(
        "file", type=str, help="MD5 Hash of the file OR URL", metavar="File"
    )

    list_parser = subparsers.add_parser(
        "list", help="List all files available for an account"
    )
    list_parser.add_argument(
        "account_id", type=str, help="Account ID", metavar="AccountID"
    )

    delete_parser = subparsers.add_parser(
        "delete", help="Delete a file from the server"
    )
    delete_parser.add_argument(
        "file", type=str, help="MD5 Hash of the file OR File URL", metavar="File"
    )
    delete_parser.add_argument(
        "-a",
        "--account_id",
        type=str,
        required=True,
        help="Account ID (Required)",
        metavar="",
        dest="account_id",
    )

    check_parser = subparsers.add_parser(
        "check", help="Check if the file already exists on the server"
    )
    check_parser.add_argument(
        "file_path", type=str, help="Path to the file", metavar="FilePath"
    )

    download_parser = subparsers.add_parser(
        "download", aliases=["dl"], help="Download a file from the server"
    )
    download_parser.add_argument(
        "file", type=str, help="MD5 Hash of the file OR Download URL", metavar="File"
    )
    download_parser.add_argument(
        "-s", "--save", type=str, help="Save location", metavar="", dest="save"
    )

    upload_parser = subparsers.add_parser(
        "upload", aliases=["ul"], help="Upload a file to the server"
    )
    upload_parser.add_argument(
        "file_path", type=str, help="Path to the file", metavar="FilePath"
    )
    upload_parser.add_argument(
        "-k",
        "--api_key",
        type=str,
        required=True,
        help="API Key for authentication",
        metavar="",
        dest="api_key"
    )
    upload_parser.add_argument(
        "-a", "--account_id", type=str, help="Account ID", metavar="", dest="account_id"
    )

    args = parser.parse_args()
    files_vc = FilesVC()
    tablefmt = args.tablefmt

    if args.command == "info":
        print()
        try:
            match = re.search(r"\b[a-f0-9]{32}\b", args.file)
            if match:
                file_hash = match.group(0)
                file_info = files_vc.get_file_info(file_hash=file_hash)
                print(create_table(file_info, tablefmt=tablefmt), end="\n\n")
            else:
                raise FilesVCException("Error: Unable to get file hash from argument.")
        except HTTPError as e:
            if e.response.status_code == 404:
                print(f"File '{args.file}' not found on the server.\n")
            else:
                print(e, end="\n\n")
        except FilesVCException as e:
            print(e, end="\n\n")

    elif args.command == "list":
        print()
        try:
            file_infos = files_vc.list_files(account_id=args.account_id)
            for file_info in file_infos:
                print(create_table(file_info, tablefmt=tablefmt), end="\n\n")
        except (HTTPError, FilesVCException) as e:
            print(e, end="\n\n")

    elif args.command == "delete":
        print()
        try:
            match = re.search(r"\b[a-f0-9]{32}\b", args.file)
            if match:
                file_hash = match.group(0)
                message = files_vc.delete_file(
                    file_hash=file_hash, account_id=args.account_id
                )
                print(f"{message} - Hash: {file_hash}", end="\n\n")
            else:
                raise FilesVCException("Error: Unable to get file hash from argument.")
        except (HTTPError, FilesVCException) as e:
            print(e, end="\n\n")

    elif args.command == "check":
        print()
        try:
            file_info = files_vc.check_file(
                file_path=args.file_path,
                progress=display_progress,
                progress_args=(time.time(), "Hashing"),
            )
            reset_line()
            if file_info:
                print(create_table(file_info, tablefmt=tablefmt), end="\n\n")
            else:
                print(f"File '{args.file_path}' not found on the server.\n")
        except (FilesVCException, TypeError) as e:
            print(e, end="\n\n")

    elif args.command in ["download", "dl"]:
        print()
        try:
            match = re.search(r"\b[a-f0-9]{32}\b", args.file)
            if match:
                file_hash = match.group(0)
                file_path = files_vc.download_file(
                    file_hash=file_hash,
                    save_path=args.save,
                    progress=display_progress,
                    progress_args=(time.time(), "Downloading"),
                )
                reset_line()
                print(f"Downloaded to: {file_path}", end="\n\n")
            else:
                raise FilesVCException("Error: Unable to get file hash from argument.")
        except (TypeError, FilesVCException, HTTPError) as e:
            print(e, end="\n\n")

    elif args.command in ["upload", "ul"]:
        print()
        try:
            file_info = files_vc.check_file(
                file_path=args.file_path,
                progress=display_progress,
                progress_args=(time.time(), "Hashing"),
            )
            reset_line()
            if file_info:
                print("File already exists on the server.")
                print(create_table(file_info, tablefmt=tablefmt), end="\n\n")
            else:
                message, file_info = files_vc.upload_file(
                    file_path=args.file_path,
                    api_key=args.api_key,
                    account_id=args.account_id,
                    progress=display_progress,
                    progress_args=(time.time(), "Uploading"),
                )
                reset_line()
                print(message)
                print(create_table(file_info, tablefmt=tablefmt), end="\n\n")
        except (FilesVCException, TypeError) as e:
            print(e, end="\n\n")

    else:
        parser.print_help()

    sys.exit(0)


if __name__ == "__main__":
    main()
