import pandas as pd
import requests
import numpy as np
from io import StringIO

def fetch_EU_data(base_url, wanted_data, countries, dataset_key, raw_datasets_dict, processed_datasets_dict, frequency):
    df_collect = pd.DataFrame()
    for country_code, country_name in countries.items():
        url = base_url + wanted_data.format(country_code=country_code)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Data not found for {country_name} ({country_code}). Adding empty column.")
            df_collect[country_name] = np.nan
            continue

        df_country = pd.read_csv(StringIO(response.text), sep='\t')
        df_country = df_country.dropna(how='all').reset_index(drop=True)

        if df_country.empty:
            print(f"All data for {country_name} ({country_code}) are empty. Adding empty column.")
            df_collect[country_name] = np.nan
            continue

        data_columns = df_country.columns[1:]
        df_collect[country_name] = df_country[data_columns].iloc[0]

    df_collect.replace(': ?', pd.NA, regex=True, inplace=True)
    df_collect.index = df_collect.index.astype(str).str.strip()

    if frequency == 'Q':
        df_collect.index = pd.PeriodIndex(df_collect.index, freq='Q').to_timestamp()
    elif frequency == 'M':
        df_collect.index = pd.PeriodIndex(df_collect.index, freq='M').to_timestamp()
    elif frequency == 'A':
        df_collect.index = pd.PeriodIndex(df_collect.index, freq='A').to_timestamp()

    df_collect = df_collect.replace({ '<NA>': np.nan, ' p': '' }, regex=True)
    df_collect.index = pd.to_datetime(df_collect.index)
    df_collect = df_collect[df_collect.index.year >= 1995]

    for column in df_collect.columns:
        df_collect[column] = pd.to_numeric(df_collect[column], errors='coerce')

    raw_datasets_dict[dataset_key] = df_collect.copy()

    if frequency in ['Q', 'M']:
        def aggregate_func(col):
            if dataset_key == "Gross domestic product at market prices":
                return col.sum()
            else:
                return col.mean()
        df_collect = df_collect.resample('A').apply(aggregate_func)

    df_collect.index = pd.to_datetime(df_collect.index.year, format='%Y')
    processed_datasets_dict[dataset_key] = df_collect
