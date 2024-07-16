import pandas as pd

if __name__ == '__main__':
    data = {
        'Name': ['John', 'Alice', 'Bob'],
        'Age': [25, 30, 35],
        'City': ['New York', 'London', 'Paris']
    }

    df = pd.DataFrame(data)
    print(df)
