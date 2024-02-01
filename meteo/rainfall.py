import pandas as pd
import requests
from requests.exceptions import HTTPError, JSONDecodeError
from io import StringIO
from datetime import datetime, timedelta


def read_rainfall_data(device, url=None):
    headers = {'Accept': 'application/json'}
    query = f'https://meter.ac/gs/meteo/{device}/data-rain.php'
    df_rainfall = pd.DataFrame()
    try:
        response = requests.get(query, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # Check if the response contains JSON data
        if response.headers.get('content-type') == 'application/json':
            data2 = response.json()
        else:
            # read response as a txt file
            # print("Response does not contain JSON data. Status code:", response.status_code)
            df_rainfall = pd.read_csv(StringIO(response.text), sep="[;, ]+", engine='python')

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except JSONDecodeError as json_err:
        print(f"JSON decoding error occurred: {json_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return df_rainfall


def amount_precipitation(df, interval_h=24, rainfall_column='rainfall', date_column='Date/Time'):
    """
    Calculate the total precipitation for each specified time interval in the given DataFrame.
    This function is create to recalculate Precipitation quantity in mm from tipping bucket devices.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame containing columns 'Date/Time' and 'rainfall'.
    - interval_hours (int): Time interval in hours for calculating precipitation. Default is 24 hours.
    - rainfall_column (str): Name of the column containing rainfall data. Default is 'rainfall'.
    - date_column (str): Name of the column containing date and time information. Default is 'Date/Time'.

    Returns:
    pandas.DataFrame: A new DataFrame with columns 'Date' and 'PQ',
                      where 'Date' represents the start date of each specified period,
                      and 'PQ' represents the Precipitation quantity in mm for that period.

    Example:
    --------
     df = pd.DataFrame({'Date/Time': ['2023-11-30 00:00:00', '2023-11-30 06:00:00', '2023-12-01 00:00:00'],
                        'rainfall': [20, 15, 30]})
     # Calculate precipitation for 24 hours
     result_24h = amount_precipitation(df)
     print(result_24h)
                    Date  PQ
    0 2023-11-30 00:00:00   7.0
    1 2023-12-01 00:00:00  30.0

     # Calculate precipitation for 48 hours
     result_48h = amount_precipitation(df, interval_hours=48)
     print(result_48h)
                    Date    PQ
    0 2023-11-30 00:00:00  35.0
    """

    df['Date'] = [d.date() for d in df[date_column]]
    df['Date'] = pd.to_datetime(df['Date'])

    result_list = []
    if interval_h == 0:
        interval_h = 0.0167

    for start_date in pd.date_range(start=df['Date'].min(), end=df['Date'].max(), freq='24h'):
        end_date = start_date + timedelta(hours=interval_h)

        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] < end_date)]
        calc = sum(filtered_df[rainfall_column] / 10 * 0.2)
        res = {'Date': start_date, 'PQ': calc}
        result_list.append(res)
    result_df = pd.DataFrame(result_list)

    return result_df


def find_rain_periods(df, rainfall_col, threshold=0.3, start_window=5, stop_window=10, date_column='Date/Time'):
    """
    Find start and stop points of rain periods in the given DataFrame.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame containing rainfall column and date column.
    - rainfall_col (str): Name of the column with rainfall data.
    - threshold (float): Threshold value for 'PQ' to indicate the start of rain. Default is 0.3.
    - start_window (int): Number of previous values to consider for starting rain. Default is 5.
    - stop_window (int): Number of consecutive values after starting rain to consider for stopping rain. Default is 10.
    - date_column (str): Name of the column containing date and time information. Default is 'Date/Time'.

    Returns:
    pandas.DataFrame: A new DataFrame with columns 'Start_Time', 'Stop_Time', and 'Duration',
                      representing the start time, stop time, and duration of each rain period.
    """

    rain_periods = []

    start_time = None
    consecutive_zeros = 0
    df = df.reset_index(drop=True)

    for index, row in df.iterrows():
        current_value = row[rainfall_col]
        next_value = df.at[index + 1, rainfall_col] if index + 1 < len(df) else None
        previous_value = df.at[index - 1, rainfall_col] if index != 0 else None
        if next_value is None:
            continue
        if previous_value is None:
            continue

        if (next_value - current_value) >= 0.01:
            if start_time is None:
                start_time = pd.to_datetime(row[date_column])
                stop_time = None
                consecutive_zeros = 0

        elif next_value == current_value and start_time is not None:
            consecutive_zeros += 1
            if consecutive_zeros == stop_window:
                stop_time = pd.to_datetime(row[date_column]) - pd.to_timedelta(stop_window, unit='minutes')
                rain_periods.append({'Start_Time': start_time, 'Stop_Time': stop_time,
                                     'Duration min': (stop_time - start_time).total_seconds() / 60})
                start_time = None
        else:
            consecutive_zeros = 0

    result_df = pd.DataFrame(rain_periods)
    return result_df


def sum_by_period(df, rainfall_col, interval_hours=24, date_column='Date/Time'):
    result_list = []

    for start_date in pd.date_range(start=df[date_column].min(), end=df[date_column].max(), freq=f'{interval_hours}h'):
        end_date = start_date + timedelta(hours=interval_hours)

        filtered_df = df[(df[date_column] >= start_date) & (df[date_column] < end_date)]
        calc = sum(filtered_df[rainfall_col])
        res = {'Date': start_date, 'PQ': calc}
        result_list.append(res)
    result_df = pd.DataFrame(result_list)
    return result_df
