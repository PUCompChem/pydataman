import pandas as pd
import requests
from matplotlib import pyplot as plt
from requests.exceptions import HTTPError, JSONDecodeError
from io import StringIO
from datetime import datetime, timedelta
import plotly.subplots as sp
import plotly.express as px


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
    result_list = []
    if interval_h == 0:
        for index, row in df.iterrows():
            calc = row[rainfall_column] / 10 * 0.2
            res = {date_column: row[date_column], 'pq': calc}
            result_list.append(res)
    else:
        interval_minutes = interval_h * 60

        for start_date in pd.date_range(start=df[date_column].min(), end=df[date_column].max(), freq=f'{interval_minutes}T'):
            end_date = start_date + pd.Timedelta(minutes=interval_minutes)

            filtered_df = df[(df[date_column] >= start_date) & (df[date_column] < end_date)]
            calc = sum(filtered_df[rainfall_column] / 10 * 0.2)
            res = {date_column: start_date, 'pq': calc}
            result_list.append(res)

    result_df = pd.DataFrame(result_list)

    return result_df


def find_rain_periods(df, rainfall_col, threshold=0.01, stop_window=10, date_column='Date/Time'):
    """
    Detects periods of rainfall in a DataFrame based on specified criteria.

    Parameters: df (DataFrame): The DataFrame containing rainfall data. rainfall_col (str): The name of the column
    containing rainfall data. threshold (float, optional): The threshold value to consider as rainfall. Default is
    0.01. stop_window (int, optional): The window size (in minutes) to consider as the end of rainfall if no rain is
    detected. Default is 10. date_column (str, optional): The name of the column containing datetime information.
    Default is 'Date/Time'.

    Returns:
        DataFrame: A DataFrame containing the detected rainfall periods with columns:
            - Start_Time: The start time of the rainfall period.
            - Stop_Time: The stop time of the rainfall period.
            - Duration_(min): The duration of the rainfall period in minutes.
            - Amount_Rainfall_(mm): The total amount of rainfall during the period in millimeters.
    """
    rain_periods = []

    start_time = None
    consecutive_zeros = 0

    for index, row in df.iterrows():
        current_value = row[rainfall_col]
        next_value = df.at[index + 1, rainfall_col] if index + 1 < len(df) else None

        if next_value is None:
            if start_time is not None:
                stop_time = row[date_column]
                rainfall_sum = df[(df[date_column] >= start_time) & (df[date_column] <= stop_time)][rainfall_col].sum()
                rain_periods.append({'Start_Time': start_time,
                                     'Stop_Time': stop_time,
                                     'Duration_(min)': (stop_time - start_time).total_seconds() / 60,
                                     'Amount_Rainfall_(mm)': rainfall_sum})
            break

        # if abs(next_value - current_value) >= threshold:
        if round(abs(next_value - current_value), 10) >= threshold:
            if start_time is None:
                start_time = pd.to_datetime(row[date_column])

            consecutive_zeros = 0

        elif next_value == current_value and start_time is not None:
            consecutive_zeros += 1
            if consecutive_zeros == stop_window:
                stop_time = pd.to_datetime(row[date_column])
                # stop_time = pd.to_datetime(row[date_column]) - pd.to_timedelta(stop_window, unit='minutes')
                rainfall_sum = df[(df[date_column] >= start_time) & (df[date_column] <= stop_time)][rainfall_col].sum()
                rain_periods.append({'Start_Time': start_time,
                                     'Stop_Time': stop_time,
                                     'Duration_(min)': (stop_time - start_time).total_seconds() / 60,
                                     'Amount_Rainfall_(mm)': rainfall_sum})
                start_time = None

    return pd.DataFrame(rain_periods)


def subtract_next_value(df, column):
    """
    Subtract each next value from the previous value in the given column of the DataFrame.

    Parameters:
    - df (pandas.DataFrame): Input DataFrame.
    - column (str): Name of the column from which values will be subtracted.

    Returns:
    pandas.DataFrame: DataFrame with the values subtracted.
    """
    subtracted_df = df.copy()
    subtracted_df[column] = abs(subtracted_df[column] - subtracted_df[column].shift(1))
    subtracted_df.at[0, column] = 0
    return subtracted_df


def sum_by_period(df, rainfall_col, interval_hours=24, date_column='Date/Time', standard='international'):
    result_list = []

    if standard == 'bg':
        start_hour, start_minute = 7, 30  # Bulgarian standard
    else:
        start_hour, start_minute = 0, 0  # international standard

    for start_date in pd.date_range(start=df[date_column].min(), end=df[date_column].max(), freq=f'{interval_hours}h'):
        start_date = start_date.replace(hour=start_hour, minute=start_minute)
        end_date = start_date + timedelta(hours=interval_hours)

        filtered_df = df[(df[date_column] >= start_date) & (df[date_column] < end_date)]
        calc = sum(filtered_df[rainfall_col])
        res = {date_column: start_date, 'PQ (mm)': calc}
        result_list.append(res)
    result_df = pd.DataFrame(result_list)
    return result_df


def plot_precipitation(df, rainfall_column, date_column='Date/Time'):
    # if date_column != 'Date/Time':
    df['Date'] = [d.date() for d in df[date_column]]
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year

    # Plotting daily precipitation
    if len(df['Date'].dt.month.unique()) > 1:
        fig = sp.make_subplots(rows=2, cols=1, shared_xaxes=False,
                               subplot_titles=['Daily Precipitation', 'Monthly Precipitation'],
                               row_heights=[0.8, 0.2])

        daily_precipitation = px.bar(df, x='Date', y=rainfall_column,
                                     # color='Month',
                                     labels={rainfall_column: 'Rainfall (mm)'},
                                     hover_data={'Date': True})

        daily_precipitation.update_xaxes(
            dtick="M1",
            tickformat="%b\n%Y",
            ticklabelmode="period")

        # Add daily precipitation subplot
        for trace in daily_precipitation.data:
            fig.add_trace(trace, row=1, col=1)

        # Calculate the sum of precipitation for each month and year
        monthly_sum = df.groupby(['Year', 'Month'])[rainfall_column].sum().reset_index()

        # Plotting monthly sum with the same color palette
        monthly_sum_chart = px.bar(monthly_sum, x='Month', y=rainfall_column,
                                   # facet_col='Year',
                                   # text='Year',
                                   labels={rainfall_column: 'Monthly Sum'},
                                   hover_data={'Month': True, 'Year':True})

        monthly_sum_chart.update_xaxes(
            dtick="M1",
            tickformat="%b\n%Y",
            ticklabelmode="period")

        # Use the same color palette as the first subplot
        for i, trace in enumerate(monthly_sum_chart.data):
            fig.add_trace(trace, row=2, col=1)

        fig.update_yaxes(title_text='Precipitation (mm)', row=1, col=1)
        fig.update_yaxes(title_text='Precipitation (mm)', row=2, col=1)
        return fig

    else:
        daily_precipitation = px.bar(df, x='Date', y=rainfall_column,
                                     # color='Date',
                                     labels={rainfall_column: 'Rainfall (mm)'},
                                     hover_data={'Date': True})

        daily_precipitation.update_xaxes(
            dtick='D1',
            tickformat="%d-%m",
            ticklabelmode="period")

        daily_precipitation.update_layout(xaxis_title='Date', yaxis_title='Precipitation (mm)')
        return daily_precipitation


def plot_rainfall_intensity(df, x_col, y_col, device, threshold=0.0001):
    plt.figure(figsize=(10, 6))

    filtered_df = df[df[y_col] >= threshold]

    plt.plot(filtered_df[x_col], filtered_df[y_col], marker='o', linestyle='', markersize=7,
             markerfacecolor='MidnightBlue', markeredgewidth=0.1, markeredgecolor='white')

    plt.xlabel('Date and time')
    plt.ylabel('Rainfall (mm)')
    plt.title(f'Rainfall Intensity for device: {device}')
    plt.grid(True, color='gray', linestyle='-', linewidth=0.1)

    return plt
