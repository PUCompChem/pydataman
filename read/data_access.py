import requests
import csv
import pandas as pd


def read_metadata(request_url):
    response_nodes = requests.get(request_url)

    if response_nodes.status_code != 200:
        print("Status code ",response_nodes.status_code)
    data_nodes = response_nodes.content.decode('utf-8')

    meta_data = list(csv.reader(data_nodes.splitlines(), delimiter=','))
    df = pd.DataFrame(meta_data[1:], columns=meta_data[0])
    return df
