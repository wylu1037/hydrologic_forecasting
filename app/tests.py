# Create your tests here.

import pytesseract
from PIL import Image

from app.service.app_service import write_upstream_water_level
from app.tools import is_two_decimal_number, datetime_to_timestamp
from hydrologic_forecasting.settings import BASE_DIR


def main():
    with Image.open(f"{BASE_DIR}/storage/water.png") as img:
        text = pytesseract.image_to_string(img)
        arr = text.split('\n\n')
        times = arr[0].splitlines()
        upstream_water_level = arr[1].splitlines()
        downstream_water_level = arr[2].splitlines()

        for i in range(len(times)):
            if len(times[i]) == 11:
                start_timestamp = datetime_to_timestamp(f'2024-{times[i]}:00')
                break

        print(start_timestamp)

        for i in range(len(upstream_water_level)):
            if is_two_decimal_number(upstream_water_level[i]):
                print(float(upstream_water_level[i]))
            elif i + 1 < len(upstream_water_level) and is_two_decimal_number(downstream_water_level[i + 1]):
                print(float(downstream_water_level[i + 1]))
            else:
                print(0)

        for i in range(len(downstream_water_level)):
            if is_two_decimal_number(downstream_water_level[i]):
                print(float(downstream_water_level[i]))
            elif i + 1 < len(downstream_water_level) and is_two_decimal_number(upstream_water_level[i + 1]):
                print(float(upstream_water_level[i + 1]))
            else:
                print(0)


if __name__ == '__main__':
    res = write_upstream_water_level("", [{
        "station": "谏壁闸",
        "datetime": "2024-07-24 20:00:00",
        "data": "6.85"
    },
        {
            "station": "谏壁闸",
            "datetime": "2024-07-24 19:00:00",
            "data": "6.49"
        }, ])
    print(res)
