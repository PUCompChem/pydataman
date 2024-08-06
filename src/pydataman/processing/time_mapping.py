import pandas as pd
import numpy as np


def time_mapping(data_node1, data_node2, feature, timestamp, closest_min=10):
    """
    Maps the values of a specified feature from one time series to another based on closest timestamps.

    Parameters:
    -----------
    data_node1 : pandas.DataFrame
        The DataFrame containing the source time series data.

    data_node2 : pandas.DataFrame
        The DataFrame containing the target time series data to which values will be mapped.

    feature : str
        The name of the feature (column) whose values will be mapped.

    timestamp : str
        The name of the timestamp column in both DataFrames.

    closest_min : int, optional
        The maximum time difference in minutes to consider a timestamp as closest. Default is 10.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the mapped values of the specified feature from data_node1 to data_node2.

    Notes:
    ------
    - Both data_node1 and data_node2 DataFrames are expected to have timestamps sorted in ascending order.
    - If a timestamp from data_node1 cannot be matched with at least two timestamps from data_node2 within
      the closest_min threshold, the mapped value for that timestamp will be NaN.
    - The mapping algorithm calculates the mapped value (S) using linear interpolation between the two closest
      timestamps in data_node2, based on their values and time differences.

    S(t) = (t - t1) * (s2 - s1) / (t2 - t1) + s1

    where:
    - t: Timestamp from data_node1
    - t1, t2: First and second closest timestamps from data_node2
    - s1, s2: Feature corresponding to t1 and t2 from data_node2

    """

    df_node1 = data_node1.set_index(timestamp)
    df_node2 = data_node2.set_index(timestamp)

    mapped_features = []

    for t1_idx, t1 in enumerate(df_node1.index):
        closest_idx = np.abs((df_node2.index - t1).total_seconds() / 60) <= closest_min
        closest_timestamps = df_node2.index[closest_idx]
        if len(closest_timestamps) < 2:
            mapped_features.append([t1, np.nan])
            continue

        time_diffs = np.abs((closest_timestamps - t1).total_seconds())
        sorted_indices = np.argsort(time_diffs)
        t1_closest = closest_timestamps[sorted_indices[0]]
        t2_closest = closest_timestamps[sorted_indices[1]]
        s1 = df_node2.loc[t1_closest, feature]
        s2 = df_node2.loc[t2_closest, feature]
        t_diff = (t2_closest - t1_closest).total_seconds() / 60

        if t_diff == 0:
            t_diff = 1

        S = ((t1 - t1_closest).total_seconds() / 60) * (s2 - s1) / t_diff + s1

        mapped_features.append([t1, S])

    mapped_df_node2 = pd.DataFrame(mapped_features, columns=[timestamp, feature])

    return mapped_df_node2
