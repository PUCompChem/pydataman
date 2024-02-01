import pandas as pd
from ioutils.meterac.data_access import read_metadata
from meteo.rainfall import read_rainfall_data, amount_precipitation, find_rain_periods, sum_by_period
from processing.convert_units import convert_unix_time
from processing.filters import filter_df_by_date_range

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

df_meteo = read_metadata('https://meter.ac/gs/metadata/meteo.csv')
metadata_dict = df_meteo.set_index('MeteoID')[['Location']].to_dict(orient='index')

device = 'M08'

rainfall_df = read_rainfall_data(device)

convert_unix_time(rainfall_df, 'unixtime')
filtered_df = filter_df_by_date_range(rainfall_df, '2024-01-22', '2024-01-30')

pq_df = pd.DataFrame()
if device == 'M01':
    pq_df = amount_precipitation(filtered_df)
# rain_period = find_rain_periods(filtered_df, 'pq', date_column='Date')
# print(rain_period)


rain_period2 = find_rain_periods(filtered_df, 'pq')
print(rain_period2)
print(filtered_df.tail())

sum_df = sum_by_period(filtered_df, 'pq', interval_hours=10)
print('summing')
print(sum_df)
