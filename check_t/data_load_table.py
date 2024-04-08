from pandas_datareader.fred import FredReader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_fred_data(freq, typedef):
    
    # Read in Excel data
    bankruptcy_data = pd.read_excel('bankruptcy_raw.xlsx', sheet_name='annual', index_col=0)
    bankruptcy_data.index = pd.to_datetime(bankruptcy_data.index, format='%Y')
    bankruptcy_data = bankruptcy_data.resample(freq).mean()  # Resample to the desired frequency

    charge_off_excel = pd.read_excel('fed_liabilities_summary.xlsx', sheet_name='import', index_col=0)
    charge_off_excel.index = pd.to_datetime(charge_off_excel.index, format='%Q')
    charge_off_excel = charge_off_excel.resample(freq).mean()  # Resample to the desired frequency


    # Dictionary of FRED series to fetch
    series = {
        'GDPC1': 'Y',              # Real GDP (Quarterly)
        'GDP': 'Y_nominal',        # Nominal GDP (Quarterly)
        'GDPC1': 'Y',                # Real GDP (Quarterly)
        'PCEC': 'C',               # consumption (Quarterly)    
        'GCEC1': 'G',                # gov. expen (Quarterly)    
        'GPDIC1': 'I',               # investment (Quarterly)   
        'PAYEMS': 'N',               # Labor Force (Monthly)   
        'CORCACBS': 'CO_rate',           # Charge-offs (Quarterly)   
        'HCCSDODNS': 'D',              # Household Debt (Quarterly)
        # 'LES1252881600Q': 'W_median',       # Median Hourly Earnings (Monthly)
        # 'AHETPI': 'W_average',               # Average Hourly Earnings (Monthly)
        'CES3000000008': 'W_manu',          # Manufacturing Wage (Monthly)
        'PCEPI': 'PCE',               # Inflation (Monthly)
        'CPIAUCSL': 'CPI',            # Inflation (Monthly)
        'FEDFUNDS': 'i',             # Interest Rate (Monthly)
        'A074RC1Q027SBEA': 'tax',    # Income Tax (Quarterly)
        'GFDEBTN': 'BG',              # Gov. Debt (Quarterly)
    }

    # Fetch FRED series data
    df = FredReader(series.keys(), start='1947').read().rename(series, axis='columns')
    gdpdef = FredReader('GDPDEF', start='1947').read()  # Fetch GDP deflator

    # Adjust to freq 
    df = df.resample(freq).mean()

    # make numbers consistent
    df['Y']=df['Y']*1000000000
    df['Y_nominal']=df['Y_nominal']*1000000000
    df['C']=df['C']*1000000000 
    df['G']=df['G']*1000000000 
    df['I']=df['I']*1000000000
    df['N']=df['N']*1000
    df['D']=df['D']*1000000000 
    df['tax']=df['tax']*1000000000
    df['BG']=df['BG']*1000000

    # Insert bankruptcy and charge off data into DataFrame
    df = df.merge(bankruptcy_data.iloc[:, 0].to_frame('BK'), left_index=True, right_index=True, how='left')

    df = df.merge(charge_off_excel.iloc[:, 0].to_frame('CO_level'), left_index=True, right_index=True, how='left')
    df['CO_level']=df['CO_level']*1000000


    # save nominal series for later use
    df['D_nominal'] = df['D']
    df['BG_nominal'] = df['BG']
    df['tax_nominal'] = df['tax']
    df['W_manu_nominal'] = df['W_manu']


    # deflate nominal series with CPI 
    df['C']=df['C']/ (df['CPI']/100)
    df['D'] = df['D']/ (df['CPI']/100) 
    df['BG'] = df['BG']/ (df['CPI']/100)
    df['tax'] = df['tax']/ (df['CPI']/100)
    df['W_manu'] = df['W_manu']/ (df['CPI']/100)
    df['CO_level'] = df['CO_level']/ (df['CPI']/100)

    # calculate growth rate nominal manf.
    df['Piw_manu_perc'] = df['W_manu_nominal'].pct_change(4) * 100
   
    # create ofther needed vars
    df['D/Y'] = (df['D_nominal']/df['Y_nominal'])*100
    df['BG/Y'] = (df['BG_nominal']/df['Y_nominal'])*100

    # Interpolate missing data
    if freq == 'Q':
        df.index.name = 'date'
        # interpolate missing data series
        df['BK'].interpolate(inplace=True)

    # create ofther needed vars after interpolation
    df['BK/N'] = (df['BK']/df['N'])*100
    
    return df

