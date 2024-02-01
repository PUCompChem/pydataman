import pandas as pd
from datetime import datetime, timedelta


def filter_df_by_date_range(df, start_date=None, end_date=None, last_year=False, last_month=False,
                            date_column='Date/Time'):
    """
    Filter DataFrame based on the specified date range.

    Parameters:
    - df: pandas DataFrame
    - start_date: str, start date in 'YYYY-MM-DD' format (optional)
    - end_date: str, end date in 'YYYY-MM-DD' format (optional)
    - last_year: bool, if True, filter based on the last year
    - last_month: bool, if True, filter based on the last month
    - date_column: str, the name of the date column in the DataFrame

    Returns:
    - pandas DataFrame, filtered based on the specified date range
    """

    filtered_df = pd.DataFrame()

    if start_date and end_date:
        df['Date'] = [d.date() for d in df[date_column]]
        df['Date'] = pd.to_datetime(df['Date'])
        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    elif last_year:
        current_year = datetime.now().year
        filtered_df = df[df[date_column].dt.year == current_year - 1]

    elif last_month:
        current_date = datetime.now()
        last_month_date = current_date - timedelta(days=current_date.day)
        filtered_df = df[
            (df[date_column].dt.year == last_month_date.year) &
            (df[date_column].dt.month == last_month_date.month)
            ]

    else:
        return df
    return filtered_df
