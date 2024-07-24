import glob
import os.path
from datetime import datetime, timedelta


def datetime_to_timestamp(time_string):
    """
    Converts a datetime string to a timestamp.

    Args:
        time_string (str): The time string to convert.

    Returns:
        int: The timestamp. Example: 649382400
    """
    time_obj = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    start_time = datetime(2001, 1, 1, 0, 0, 0)
    time_diff = time_obj - start_time
    return time_diff.total_seconds()


def timestamp_to_datetime(timestamp_seconds):
    """
    Converts a timestamp in seconds into a datetime string.

    Args:
        timestamp_seconds (int): The timestamp in seconds.

    Returns:
        string: The datetime string. Example: 2021-07-30 00:00:00
    """
    start_time = datetime(2001, 1, 1, 0, 0, 0)
    target_time = start_time + timedelta(seconds=timestamp_seconds)
    return target_time.strftime("%Y-%m-%d %H:%M:%S")


def search_file(directory, pattern):
    """
    Search a directory for all files matching a pattern.

    Args:
        directory (str): The directory to search.
        pattern (str): The pattern to search for.
    """
    search_pattern = os.path.join(directory, f'*{pattern}')
    file = glob.glob(search_pattern)
    if len(file) == 0:
        raise FileNotFoundError
    return file[0]


if __name__ == '__main__':
    timestamp = 649382400
    time_str = timestamp_to_datetime(timestamp)
    print(time_str)
