import pandas as pd
import numpy as np

def create_country_stats_table(datasets_dict, dataset_key):
    if dataset_key not in datasets_dict:
        print(f"Dataset key '{dataset_key}' not found in the dictionary.")
        return None

    df = datasets_dict[dataset_key]
    rows = []
    for country in df.columns:
        if country == df.index.name:
            continue

        latest_data = df[country].dropna()
        if not latest_data.empty:
            latest_value = latest_data.iloc[-1]
            latest_date = latest_data.index[-1]
        else:
            latest_value, latest_date = np.nan, pd.NaT

        latest_date = df.index.max()
        if not isinstance(latest_date, pd.Timestamp):
            print(f"Warning: Latest date for {country} is not a datetime object: {latest_date}")
            continue

        prev_year_date = latest_date - pd.DateOffset(years=1)
        prev_year_value = df[country][df.index == prev_year_date]
        prev_year_value = prev_year_value.iloc[0] if not prev_year_value.empty else np.nan

        rows.append({'Country': country, 'Latest Value': latest_value,
                     'Date of Latest Value': latest_date,
                     'Previous Year Value': prev_year_value,
                     'Date of Previous Year Value': prev_year_date})

    table = pd.DataFrame(rows)
    return table
