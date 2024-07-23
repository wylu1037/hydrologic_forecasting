from datetime import datetime, timedelta


def datetime_to_timestamp(time_string):
    time_obj = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    start_time = datetime(2001, 1, 1, 0, 0, 0)
    time_diff = time_obj - start_time
    return time_diff.total_seconds()


def timestamp_to_datetime(timestamp_seconds):
    start_time = datetime(2001, 1, 1, 0, 0, 0)
    target_time = start_time + timedelta(seconds=timestamp_seconds)
    return target_time.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    timestamp = 649382400
    time_str = timestamp_to_datetime(timestamp)
    print(time_str)
