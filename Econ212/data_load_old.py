from pandas_datareader.fred import FredReader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_historical_cpi():
    #source: https://www.measuringworth.com/datasets/uscpi/
    df=pd.read_csv('Import/USCPI_1774-2020.csv')
    df.index = df["Year"]
    df.index.name = 'year'
    df.drop(columns="Year", inplace=True)
    return df

def get_state_u_data(freq):
    statelist=["AK","AL","AR","AZ","CA","CO","CT","DE","FL","GA","HI","IA","ID","IL","IN","KS","KY","LA","MA","MD",
            "ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","RI","SC","SD",
            "TN","TX","UT","VA","VT","WA","WI","WV","WY"]
    # To get GDP: state+"RGSP"
    # To get POP: state+"POP"
    # To get UR: state+"UR"

    udict={}
    # Populate a dict with Fred keys indexed by state key
    for i in statelist:
        udict[i+"UR"]=i

    df = FredReader(udict.keys(), start='1947').read().rename(udict, axis='columns')
    df = df.resample('Q').mean()
    return df

def get_fred_data(freq,typedef):
    """
        Use freq='Q' for quarterly, 'A' for annual
        Use typedef='own_def' for own deflator, otherwise (same_def) deflates all nominal series by same deflator
    """
    series =   {
            # Nominal quantities
            'GDP': 'yn',                    # Nominal GDP 
            'PCEC': 'cn',                   # Nominal PCE [note: we use quarterly not to mess up frequencies otherwise]
            'GCE': 'gn',                    # Nominal G
            'GPDI': 'in',                   # Nominal I 
            'NETEXP': 'nxn',                # Nominal NX
            'IMPGS': 'impn',                # Nominal IMP
            'EXPGS': 'expn',                # Nominal EXP
            # Real chained quantities
            'GDPC1': 'y',                   # Real GDP chained SAAR 2012
            'PCECC96': 'c',                 # Real PCE chained SAAR 2012
            'GCEC1': 'g',                   # Real G chained SAAR 2012
            'GPDIC1': 'i',                  # Real I chained SAAR 2012
            'NETEXC': 'nx',                 # Real NX chained SAAR 2012
            'IMPGSC1': 'imp',               # Real imports chained SAAR 2012
            'EXPGSC1': 'exp',               # Real exports chained SAAR 2012
            #Other
            'HCCSDODNS':'debt',              # Households and Nonprofit Organizations; Consumer Credit [may want to change]
            'TTLHH': 'hh',                   # Total number of households
            'POP': 'pop',                    # Total population (starts 1952, from Census)
            'TERMCBCCINTNS': 'rcc',          # Commercial Bank Interest Rate on Credit Card Plans [only from 1996]
            'GDPDEF': 'gdpdef',              # GDP deflator
            'DPCCRV1Q225SBEA': 'pce_infl',   # Inflation in PCE excluding food-energy chain-type
            'CPIAUCSL': 'cpi',               # Consumer price index all urban
            'M1SL': 'm1',                    # M1 money stock
            'M2SL': 'm2',                    # M2 money stock 
            'CURRCIR': 'currcir',            # Currency in circulation
            'FEDFUNDS': 'fedfunds',          # Fed Funds rate
            'PAYEMS': 'emp',                 # All employee nonfarm, CES [150m]
            'PRS85006023': 'h',              # Avg weekly hours in nonfarm business, index 2012 (per person)
            'OPHNFB': 'labprod',             # Output per hour of all persons
            'COMPNFB': 'w',                  # Compensation per hour in nonfarm business
            'UNRATE': 'u',                   # Unemployment rate
            'USREC': 'USREC',                # NBER Recession indicator
            'RKNANPUSA666NRUG': 'k',         # Capital stock at constant prices (from Penn World tables)      
            'NGDPPOT': 'ypotn',              # Nominal potential domestic product (CBO)
            'GDPPOT': 'ypot',                # Real potential GDP
            'TOTRESNS': 'totres',            # Total reserves of depository institutions
            'IOER': 'ioer',                  # Interest rate on excess reserves (also equal to interest on required reserves)
            'DGS10':'dgs10',                 # 10 year treasury rate
            'T10YIE': 'breakeven10',         # 10 year breakeven inflation rate
            'PCND': 'nondur',                # Non-durable consumption
            'PCDG': 'dur',                   # Durable consumption
            'GPDI': 'invest',                # Investments
            'W068RCQ027SBEA': 'govexpen',    # Gov. Expenditures 
            'RKNANPUSA666NRUG': 'capitalu',  # Capital stock 
            'RTFPNAUSA632NRUG': 'solow',     # Productivity
            'B4701C0A222NBEA': 'thours',     # Total hours
            'LREM64TTUSM156S': 'emplyment',  # Employment
            'LES1252881600Q': 'mrwage'       # Median real wage
            }          

    df = FredReader(series.keys(), start='1947').read().rename(series, axis='columns')

    # get rid of annoying double month stuff
    # assert (df.resample('M').count() <= 1).all().all()
    # df = df.resample('M').mean()

    # Adjust to freq 
    df = df.resample(freq).mean()

    if freq=='M':
        # at monthly frequency, interpolate the nominal series where we have available data
        df['yn'].interpolate(method='linear', limit=2, limit_area='inside', inplace=True)
        df['cn'].interpolate(method='linear', limit=2, limit_area='inside',inplace=True)
        df['gn'].interpolate(method='linear', limit=2, limit_area='inside',inplace=True)
        df['in'].interpolate(method='linear', limit=2, limit_area='inside', inplace=True)
        df['nxn'].interpolate(method='linear', limit=2, limit_area='inside',inplace=True)
        df['impn'].interpolate(method='linear', limit=2, limit_area='inside', inplace=True)
        df['expn'].interpolate(method='linear', limit=2, limit_area='inside', inplace=True)
        df['gdpdef'].interpolate(method='linear', limit=2, limit_area='inside', inplace=True)
        
    if typedef=='same_def':
        # Use GDP deflator for everything
        df['y'] = df['yn']*100/df['gdpdef']
        df['c'] = df['cn']*100/df['gdpdef']
        df['g'] = df['gn']*100/df['gdpdef']
        df['i'] = df['in']*100/df['gdpdef']
        df['nx'] = df['nxn']*100/df['gdpdef']
        df['imp'] = df['impn']*100/df['gdpdef']
        df['exp'] = df['expn']*100/df['gdpdef']

    # If annual, return with integer indices
    if freq=='A':
        df.index = df.index.year
        df.index.name = 'year'
     
    if freq=='Q':
        df.index.name = 'date'
        # interpolate missing data series
        df['hh'].interpolate(inplace=True)
        df['k'].interpolate(inplace=True)
        
    return df

