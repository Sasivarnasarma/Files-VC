# -*- coding: utf-8 -*-

"""Python files.vc API wrapper and command line interface.

This module provides some utility functions.

@author: Sasivarnasarma
@contact: sasivarnasarma@protonmail.com
@license: MIT License, see LICENSE file

Copyright (C) 2025
"""

import time
import shutil
from datetime import datetime


def convert_to_datetime(timestamp: str) -> datetime:
    """Convert a string timestamp to a datetime object.

    Supports ISO 8601 timestamps (as returned by datetime.isoformat())
    and timestamps in the format "%Y-%m-%dT%H:%M:%SZ".

    :param timestamp: The timestamp to convert.
    :type timestamp: str
    :raises ValueError: If the timestamp is not in a recognized format.
    :return: A datetime object representing the timestamp.
    :rtype: datetime
    """
    for fmt in (
        datetime.fromisoformat,
        lambda ts: datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"),
    ):
        try:
            return fmt(timestamp)
        except ValueError:
            continue

    raise ValueError(f"Unrecognized timestamp format: {timestamp}")


def get_readable_file_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable file size (KB, MB, GB, TB and PB.).

    :param size_bytes: The size of the file in bytes.
    :type size_bytes: int
    :return: A string with the size of the file in a human-readable
        format.
    :rtype: str
    """
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    while size_bytes >= 1024:
        size_bytes /= 1024
        index += 1
    if index >= len(units):
        return "File too large"
    return f"{size_bytes:.2f} {units[index]}"


def get_readable_time(duration: float) -> str:
    """Convert seconds to a human-readable duration (days, hours, minutes and
    seconds.).

    :param duration: The duration in seconds.
    :type duration: float
    :return: A string with the duration in a human-readable format.
    :rtype: str
    """
    if duration == float("inf"):
        return "Inf"
    if duration < 60:
        return f"{duration:.1f}s"

    result = ""
    seconds = int(duration)
    days, remainder = divmod(seconds, 86400)
    if days > 0:
        result += f"{days}d"
    hours, remainder = divmod(remainder, 3600)
    if hours > 0:
        result += f"{hours}h"
    minutes, seconds = divmod(remainder, 60)
    if minutes > 0:
        result += f"{minutes}m"
    result += f"{seconds}s"
    return result


def display_progress(
    current_size: int,
    total_size: int,
    start_time: float,
    process_text: str,
    end: bool = False,
) -> None:
    """Display a dynamic progress bar indicating the progress of a file
    operation.

    :param current_size: The current size of the processed portion of
        the file in bytes.
    :type current_size: int
    :param total_size: The total size of the file in bytes.
    :type total_size: int
    :param start_time: The start time of the operation as a timestamp.
    :type start_time: float
    :param process_text: A descriptive text for the process being
        performed.
    :type process_text: str
    :param end: A flag indicating whether the operation has completed.
        Default is False.
    :type end: bool
    :return: None
    :rtype: None The progress bar displays the percentage of completion,
        the current and total file sizes in a human-readable format, the
        speed of the operation, and the estimated time remaining and
        elapsed. It dynamically adjusts to fit the terminal width and
        updates in place.
    """
    terminal_width = shutil.get_terminal_size().columns
    if end or current_size >= total_size:
        print("\r" + " " * terminal_width, end="\r", flush=True)
        return

    if total_size <= 0:
        return

    elapsed_time = time.time() - start_time
    done_per = float(100 * current_size / total_size)

    min_bar_length = 20
    info_length = 100
    bar_length = max(min_bar_length, terminal_width - info_length)
    bar_length = (bar_length // 5) * 5

    done = int(bar_length * (current_size / total_size))
    done_bar = "■" * done
    remaining_bar = "□" * (bar_length - done)

    speed = current_size / elapsed_time if elapsed_time > 0 else 0
    speed_readable = get_readable_file_size(int(speed))
    total_readable = get_readable_file_size(total_size)
    current_readable = get_readable_file_size(current_size)
    remaining_time = (total_size - current_size) / speed if speed > 0 else float("inf")
    elapsed_readable = get_readable_time(elapsed_time)
    remaining_readable = get_readable_time(remaining_time)

    progress_text = f"\r| {process_text} [{done_bar}{remaining_bar}] {done_per:.1f}% |"
    details_text = (
        f" ({speed_readable}/s) {current_readable} of {total_readable} Done |"
    )
    eta_text = f" ETA: {remaining_readable} |"
    elapsed_text = f" Elapsed: {elapsed_readable} |"

    if len(progress_text) + len(details_text) < terminal_width:
        progress_text += details_text
    if len(progress_text) + len(eta_text) < terminal_width:
        progress_text += eta_text
    if len(progress_text) + len(elapsed_text) < terminal_width:
        progress_text += elapsed_text
    progress_text = progress_text + " " * (terminal_width - len(progress_text))

    print(progress_text, end="", flush=True)
    return


def reset_line() -> None:
    """Clears the current line in the terminal.

    This function prints a carriage return followed by a blank line that
    spans the entire width of the terminal, effectively erasing any
    existing content on the current line. It then returns the cursor to
    the beginning of the line.
    :return: None
    :rtype: None
    """
    print("\r" + " " * shutil.get_terminal_size().columns, end="\r", flush=True)
