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
        'HCCSDODNS': 'D',              # Household Debt (Quarterly)
        'LES1252881600Q': 'W_median',       # Median Hourly Earnings (Monthly)
        'AHETPI': 'W_average',               # Average Hourly Earnings (Monthly)
        'CES3000000008': 'W_manu',          # Manufacturing Wage (Monthly)
        'PCEPI': 'Pi',               # Inflation (Monthly)
        'FEDFUNDS': 'i',             # Interest Rate (Monthly)
        'A074RC1Q027SBEA': 'tax',    # Income Tax (Quarterly)
        'GFDEBTN': 'GD',              # Gov. Debt (Quarterly)
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
        df['GD'] = df['GD'] * 100 / gdpdef
        df['tax'] = df['tax'] * 100 / gdpdef  # Make sure 'gdpdef' is defined in `series`
        df['W_average'] = df['W_average'] * 100 / gdpdef  
        df['W_manu'] = df['W_manu'] * 100 / gdpdef

    # calculate growth rate of W_average and W_manu
    df['Piw_average'] = df['W_average'].pct_change() * 100
    df['Piw_manu'] = df['W_manu'].pct_change() * 100
    df['BG_Y'] = df['GD']/df['Y']


    


    # Interpolate missing data
    if freq == 'Q':
        df.index.name = 'date'
        # interpolate missing data series
        df['BK'].interpolate(inplace=True)
    
    return df

