import pandas as pd


def convert_unix_time(df, unixtime_column):
    """
    Convert Unix timestamp to human-readable date and time in a pandas DataFrame.

    Parameters:
    - df (pd.DataFrame): The pandas DataFrame containing the Unix timestamp column.
    - unixtime_column (str): The name of the column containing Unix timestamps.

    Returns:
    None

    Modifies the input DataFrame by adding three new columns:
    - 'Date/Time': Contains the converted datetime values from the Unix timestamps.
    - 'Date': Contains the date part extracted from 'Date/Time'.
    - 'Time': Contains the time part extracted from 'Date/Time'.

    Example:
     df = pd.DataFrame({'unix_timestamp': [1637088000, 1637091600, 1637095200]})
     convert_unix_time(df, 'unix_timestamp')
     print(df[['Date/Time', 'Date', 'Time']])
              Date/Time        Date      Time
    0 2021-11-16 00:00:00  2021-11-16  00:00:00
    1 2021-11-16 01:00:00  2021-11-16  01:00:00
    2 2021-11-16 02:00:00  2021-11-16  02:00:00
    """
    df.columns = df.columns.str.lower()
    df['Date/Time'] = pd.to_datetime(df[unixtime_column.lower()], unit='s')
    df['Date'] = [d.date() for d in df['Date/Time']]
    df['Date']= pd.to_datetime(df['Date'])

    df['Time'] = [d.time() for d in df['Date/Time']]
