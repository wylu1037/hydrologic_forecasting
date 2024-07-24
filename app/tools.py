import glob
import logging
import os.path
import re
from datetime import datetime, timedelta

import requests

from hydrologic_forecasting.settings import BASE_DIR


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
    return int(time_diff.total_seconds())


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


def is_two_decimal_number(number):
    """
    Checks if the given number is a decimal number.
    """
    pattern = r'^\d+\.\d{2}$'
    return bool(re.match(pattern, number))


def download_png():
    png_file = f'{BASE_DIR}/storage/water_level.png'
    try:
        response = requests.get(
            f'http://www.jsswj.com.cn:88/jsswxxSSI/static/map/chart/0/061fece4c7524ee2adcae16982229e0e_list.png?t={datetime.now().timestamp()}')
        if response.status_code == 200:
            if os.path.exists(png_file):
                os.remove(png_file)
            with open(png_file, 'wb') as f:
                f.write(response.content)
            return png_file
        else:
            logging.error("下载图片资源失败，响应：%s", response)
            raise ValueError(response)
    except Exception as e:
        logging.error("下载谏壁闸水位图片失败：%s", e)
        raise e


if __name__ == '__main__':
    download_png()
