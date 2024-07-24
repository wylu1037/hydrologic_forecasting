import json
from datetime import datetime, timedelta

import numpy as np
import pytesseract
import pytz
import requests
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup
from django.utils import timezone

from app.models import Rainfall
from app.repository.app_repository import AppRepository
from app.tools import download_png, datetime_to_timestamp, is_two_decimal_number
from hydrologic_forecasting.settings import config


# from app.models import Rainfall


def pull_data_from_dan_yang():
    """
    从中国气象网站上获取丹阳的降水数据
    """
    url = config['scheduler']['rainfall']['dan_yang']
    response = requests.get(f'{url}{datetime.now().timestamp()}')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        json_string = soup.prettify()
        response = json.loads(json_string)
        if response['code'] == 0:
            data = response['data']
            passed_chart = data['passedchart']
            for chart in passed_chart:
                # first
                time = datetime.strptime(chart['time'], '%Y-%m-%d %H:%M')
                current_tz = pytz.timezone('Asia/Shanghai')
                aware_datetime = current_tz.localize(time)
                result = Rainfall.objects.filter(station='丹阳', datetime=aware_datetime)[:1]
                if result.count() == 0:
                    rainfall = Rainfall(
                        station='丹阳',
                        datetime=aware_datetime,
                        data=chart['rain1h']
                    )
                    rainfall.save()


def pull_data_from_jian_bi_zha_png():
    """
    从谏壁闸下载上游水位和下游水位数据
    """
    png_file = download_png()
    with Image.open(png_file) as img:
        text = pytesseract.image_to_string(img)
        print(text)
        arr = text.split('\n\n')
        times = arr[0].splitlines()
        upstream_water_level = arr[1].splitlines()
        downstream_water_level = arr[2].splitlines()

        for i in range(len(times)):
            if len(times[i]) == 11:
                first_timestamp = datetime_to_timestamp(f'2024-{times[i]}:00')
                start_timestamp = first_timestamp - 60 * 60 * i
                break

        upstream_water_level = parse_string_numbers(upstream_water_level)
        downstream_water_level = parse_string_numbers(downstream_water_level)

        for i in range(24):
            time = timestamp_to_datetime(start_timestamp - i * 60 * 60)
            AppRepository.upsert_upstream_water_level('谏壁闸', time, upstream_water_level[i])
            AppRepository.upsert_downstream_water_level('谏壁闸', time, downstream_water_level[i])


def parse_string_numbers(water_level_arr):
    """
    将字符串数组的数字解析为浮点数数组
    """
    number_arr = np.zeros(len(water_level_arr), dtype=float)
    for i in range(len(water_level_arr)):
        if is_two_decimal_number(water_level_arr[i]):
            number_arr[i] = float(water_level_arr[i])
        elif i + 1 < len(water_level_arr) and is_two_decimal_number(water_level_arr[i + 1]):
            number_arr[i] = float(water_level_arr[i + 1])
        elif i + 2 < len(water_level_arr) and is_two_decimal_number(water_level_arr[i + 2]):
            number_arr[i] = float(water_level_arr[i + 2])
        elif i + 3 < len(water_level_arr) and is_two_decimal_number(water_level_arr[i + 3]):
            number_arr[i] = float(water_level_arr[i + 3])
        elif i > 0:
            number_arr[i] = float(water_level_arr[i - 1])
        else:
            number_arr[i] = 0.1

    return number_arr


def timestamp_to_datetime(timestamp_seconds):
    """
    Converts a timestamp in seconds into a datetime string.

    Args:
        timestamp_seconds (int): The timestamp in seconds.

    Returns:
        string: The datetime string. Example: 2021-07-30 00:00:00
    """
    start_time = datetime(2001, 1, 1, 0, 0, 0)
    time = start_time + timedelta(seconds=timestamp_seconds)
    return timezone.make_aware(time, timezone.get_current_timezone())


scheduler = BackgroundScheduler()

scheduler.add_job(pull_data_from_dan_yang, 'interval', seconds=60_000)
scheduler.add_job(pull_data_from_jian_bi_zha_png, 'interval', seconds=60_000)
