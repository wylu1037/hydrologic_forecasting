import pytesseract
import requests
from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup

_URL = 'http://www.jsswj.com.cn:88/jsswxxSSI/Web/Default.html?m=2'


def pull_data_from_dan_yang():
    print('丹阳\n')


def pull_data_from_jian_bi_zha():
    print('谏壁闸\n')


scheduler = BackgroundScheduler()

scheduler.add_job(pull_data_from_dan_yang, 'interval', seconds=10)
scheduler.add_job(pull_data_from_jian_bi_zha, 'interval', seconds=5)


def main():
    response = requests.get(_URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a', href=True)
        for link in links:
            print(link['href'])

    with Image.open("/Users/wenyanglu/Workspace/github/hydrologic_forecasting/app/water.png") as img:
        text = pytesseract.image_to_string(img)
        print(text)


if __name__ == '__main__':
    main()
