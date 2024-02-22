from pandas_datareader.fred import FredReader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_fred_data(freq, typedef):
    
    # Read Excel data
    bankruptcy_data = pd.read_excel('bankruptcy_raw.xlsx', sheet_name='quarterly', index_col=0)
    bankruptcy_data.index = pd.to_datetime(bankruptcy_data.index, format='%Q')
    bankruptcy_data = bankruptcy_data.resample(freq).mean()  # Resample to the desired frequency
    
    # Dictionary of FRED series to fetch
    series = {
        'GDPC1': 'Y',                # Real GDP (Quarterly)
        'PCECC96': 'C',              # Real consumption (Quarterly)    
        'GCEC1': 'G',                # Real gov. expen (Quarterly)    
        'GPDIC1': 'I',               # Real investment (Quarterly)   
        'PAYEMS': 'N',               # Labor Force (Monthly)
        # 'BANKRUPTCY': 'BK',    
        'CORCACBS': 'CO',           # Charge-offs (Quarterly)   
        'GFDEBTN': 'D',              # Fed Debt (Quarterly)
        'LES1252881600Q': 'W',       # Average Hourly Earnings (Monthly)
        'PCEPI': 'Pi',               # Inflation (Monthly)
        'FEDFUNDS': 'i',             # Interest Rate (Monthly)
        'A074RC1Q027SBEA': 'tax',    # Income Tax (Quarterly)
    }
    
    # Fetch FRED series data
    df = FredReader(series.keys(), start='1947').read().rename(series, axis='columns')
    gdpdef = FredReader('GDPDEF', start='1947').read()  # Fetch GDP deflator

    # Adjust to freq 
    df = df.resample(freq).mean()
    
    # Insert bankruptcy data into DataFrame
    df = df.merge(bankruptcy_data.iloc[:, 0].to_frame('BK'), left_index=True, right_index=True, how='left')

    # Deflate nominal series
    if typedef == 'same_def':
        df['D'] = df['D'] * 100 / gdpdef  # Make sure 'gdpdef' is defined in `series`
        df['tax'] = df['tax'] * 100 / gdpdef  # Make sure 'gdpdef' is defined in `series`

    # Interpolate missing data
    if freq == 'Q':
        df.index.name = 'date'
        # interpolate missing data series
        df['BK'].interpolate(inplace=True)


    # Reorder the DataFrame to include bankruptcy data between 'N' and 'CO'
    columns_order = ['Y', 'C', 'G', 'I', 'N', 'BK', 'CO', 'D', 'W', 'Pi', 'i', 'tax']  # Include other series names if necessary
    df = df[columns_order]
    
    return df

