import requests
import csv
import pandas as pd


def read_metadata(request_url):
    """
    Fetches metadata from a specified URL and converts it into a DataFrame.

    Parameters:
    -----------
    request_url : str
        The URL from which metadata will be fetched.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the metadata fetched from the specified URL.

    Notes:
    ------
    - The function expects the metadata to be in CSV format.
    - It sends an HTTP GET request to the provided URL to fetch the metadata.
    - If the HTTP response status code is not 200 (OK), it prints the status code.
    - The fetched metadata is then decoded from UTF-8 and converted into a DataFrame.
    - The first row of the CSV data is assumed to contain column headers.
    """

    response_nodes = requests.get(request_url)

    if response_nodes.status_code != 200:
        print("Status code ", response_nodes.status_code)
    data_nodes = response_nodes.content.decode('utf-8')

    meta_data = list(csv.reader(data_nodes.splitlines(), delimiter=','))
    df = pd.DataFrame(meta_data[1:], columns=meta_data[0])
    return df

def read_data():
    pass
