import datetime
import json

import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup

from app.models import Rainfall
from hydrologic_forecasting.settings import config

# from app.models import Rainfall

_DAN_YANG = 'http://www.nmc.cn/rest/weather?stationid=tCUFF&_='
_URL = 'http://www.nmc.cn/rest/weather?stationid=aELXI&_='


def pull_data_from_dan_yang():
    url = config['scheduler']['rainfall']['dan_yang']
    response = requests.get(f'{url}{datetime.datetime.now().timestamp()}')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        json_string = soup.prettify()
        response = json.loads(json_string)
        if response['code'] == 0:
            data = response['data']
            passed_chart = data['passedchart']
            for chart in passed_chart:
                # first
                time = datetime.datetime.strptime(chart['time'], '%Y-%m-%d %H:%M')
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


scheduler = BackgroundScheduler()

scheduler.add_job(pull_data_from_dan_yang, 'interval', seconds=60_000)


def main():
    # with Image.open("/Users/wenyanglu/Workspace/github/hydrologic_forecasting/app/water.png") as img:
    #     text = pytesseract.image_to_string(img)
    #     print(text)

    timestamp = datetime.datetime.now().timestamp()
    response = requests.get(f'{_DAN_YANG}{timestamp}')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        json_string = soup.prettify()
        response = json.loads(json_string)
        if response['code'] == 0:
            data = response['data']
            passed_chart = data['passedchart']
            for chart in passed_chart:
                # first
                result = Rainfall.objects.filter(station='丹阳', datetime=chart['time'])[:1]

                rainfall = Rainfall(
                    station='丹阳',
                    datetime=chart['time'],
                    data=chart['rain1h']
                )
                rainfall.save()


if __name__ == '__main__':
    main()
