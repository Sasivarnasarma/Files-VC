# Files.VC Python Library

An Unofficial Python wrapper and CLI tool for the Files.VC API, designed to download, upload, and manage files efficiently.

## Features

- **Command-Line Interface (CLI)** – Manage files directly from the terminal.
- **Python Library** – Easily embed `files_vc` into your Python programs.
- **Beautiful Output** – Using the `tabulate` library, provides a well-formatted table for file information.
- **Progress Tracking** – Shows real-time progress for uploads and downloads.
- **Dynamic Progress Bar** – In CLI mode, displays terminal size based progress bar with speed, remaining time, and elapsed time.
- **Error Handling** – Graceful handling of network failures and interruptions.
- **Cross-Platform** – Works on Windows, macOS, and Linux.

## Installation

Install the package from [PyPI](https://pypi.org/project/Files-VC/):

```bash
python3 -m pip install Files-VC -U
```

Ensure you have Python 3.7 or later.

---

## Using Files-VC as a Command Line Interface

Once installed, you can use the `files-vc` command to interact with the files.vc API.

```bash
files-vc --help
```

Use the `-h`/`--help` flag with any command to see the available options for that specific command.

```bash
file-vc <command> --help
```

### Usage

```bash
files-vc <command> <positional_arguments> [options]
```

#### Available Commands & Arguments

- **Common options**:
    - `-h`/`--help`: Display help
    - `-v`/`--version`: Display version information
    - `-t`/`--tablefmt`: Set File info output format
- **info**: Get file information by file hash or URL
- **list**: List all files for a given account ID
- **delete**: Delete a file from the server
    - `-a`/`--account_id`: Specify the account ID that belongs to the file. (Required)
- **check**: Check if a file already exists on the server
- **download/dl**: Download a file using its hash or URL
    - `-s`/`--save`: Specify the folder path to save the downloaded file
- **upload/ul**: Upload a file to the server
    - `k`/`--api_key`: Specify API Key for authentication. (Required) [Get API Key](https://files.vc/api)
    - `-a`/`--account_id`: Specify the account ID to upload the file

You can customize table output format using the `-t`/`--tablefmt` option, which supports formats like plain, grid, etc.
Check out the [Tabulate README](https://github.com/astanin/python-tabulate#table-format) for a list of available formats and more details.

> [!IMPORTANT]  
> To upload a file, you must provide a valid API token. [Obtain your API key from the Files.VC](https://files.vc/api)


**"This option must be used before the command."**

```	bash
files-vc --tablefmt grid <command> <args>
```

#### Examples

```bash
# Get file info
files-vc info <file_hash_or_url>
# List files for an account
files-vc list <account_id>
# Delete a file from the server
files-vc delete <file_hash_or_url> --account_id <account_id>
# Check if a file exists on the server
files-vc check /path/to/file
# Download a file (with optional save location)
files-vc download <file_hash_or_url> --save /path/to/save/location
# Upload a file (with optional account ID)
files-vc upload /path/to/file --api_key <api_key> --account_id <account_id>
```

> [!NOTE]
> After uploading, it may take a few seconds (depending on the file size) to display the file info, so please be patient.
> This is because the server takes some time to send a response.

---

## Using Files-VC in Python Programs

You can also embed Files-VC directly into your Python code:

```python
from files_vc import FilesVC

files_vc = FilesVC()

# Get file info
file_info = files_vc.get_file_info(file_hash="your_file_hash")
print(file_info.name, file_info.size)

# List files
files = files_vc.list_files(account_id="your_account_id")
for file in files:
    print(file.name, file.download_url)

# Delete a file
message = files_vc.delete_file(file_hash="your_file_hash", account_id="your_account_id")
print(message)

# Check if a file exists
file_info = files_vc.check_file(file_path="/path/to/file")
print(file_info)

# Upload a file
message, file_info = files_vc.upload_file("/path/to/file", account_id="your_account_id")
print(message, file_info.view_url)

# Download a file
downloaded_path = files_vc.download_file(file_hash="your_file_hash", save_path="/path/to/save")
print(f"File saved at {downloaded_path}")
```

---

> [!TIP]
> Always verify if the file already exists on the server using the `FilesVC().check_file(file_path}` function before uploading it.
> This will reduce unwanted bandwidth usage.
> Check the [\_\_main\_\_.py](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/__main__.py#L184-L209) file for reference/ideas.

## API Reference
**Each class and function includes a docstring. For more details, refer to it.**

### `FilesVC`

The core class for interacting with the files.vc API.

#### Methods

- `get_file_info(file_hash: str, ...) -> FileInfo`: Get information about a file. [(Docstring)](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/_main.py#L122-L136)
- `list_files(account_id: str) -> list[FileInfo]`: Retrieve a list of files for an account. [(Docstring)](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/_main.py#L158-L169)
- `delete_file(file_hash: str, account_id: str, ...) -> str`: Delete a file from the server. [(Docstring)](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/_main.py#L187-L205)
- `check_file(file_path: str, ...) -> FileInfo | None`: Check if a file already exists on the server. [(Docstring)](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/_main.py#L246-L261)
- `download_file(file_hash: str, save_path: str, ...) -> str`: Download a file by hash. [(Docstring)](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/_main.py#L298-L320)
- `upload_file(file_path: str, account_id: str, ...) -> tuple[str, FileInfo]`: Upload a file to the server. [(Docstring)](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/_main.py#L369-L387)

> [!TIP]
> The `check_file`, `download_file`, and `upload_file` functions include `progress` and `progress_args` parameters, which allow you to customize the progress.
> Check the [\_\_main\_\_.py](https://github.com/Sasivarnasarma/Files-VC/blob/main/files_vc/__main__.py) file for reference/ideas.

### `FileInfo`

Represents metadata for a file.

- `name`: File name
- `file_hash`: MD5 hash of the file
- `size`: File size in bytes
- `upload_time`: Time the file was uploaded
- `mime_type`: File's MIME type
- `download_count`: Number of downloads
- `view_url`: URL to view the file
- `download_url`: URL to download the file
- `expiration_time`: Expiration time (if any)

### Exception

- `FilesVCException`: Custom exception for handling errors related to files.vc API operations.
- `HTTPError`: Exception raised when there is an HTTP error. (Same as requests.exceptions.HTTPError)
- And other exceptions from the requests library.

---

## TODO

- [ ] **Creating tests** – Unit and integration tests for core functions.
- [ ] **Creating documentation** – Generate API documentation for better developer experience.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with your improvements.

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

### With ❤️ Made By @Sasivarnasarma
