import eurostat 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function for best linear fit
def reg_fit(Y,X, verbose=False):
    X = sm.add_constant(X)
    model=sm.OLS(Y,X)
    results = model.fit()
    if verbose:
        print(results.summary())
    return results.predict(), results.params
 
# Decadal average log growth
def decadal_average_growth(ser, dec=False):
    if dec:
        # Actual decadal growh
        t=ser.loc['1950-03-31':'1959-12-31']
        nq=t.index.size
        print('Average for 1950s :', round(np.log(t[-1]/t[0])/(nq/4),4))

        t=ser.loc['1960-03-31':'1969-12-31']
        nq=t.index.size
        print('Average for 1960s :', round(np.log(t[-1]/t[0])/(nq/4),4))

        t=ser.loc['1970-03-31':'1979-12-31']
        nq=t.index.size
        print('Average for 1970s :', round(np.log(t[-1]/t[0])/(nq/4),4))

        t=ser.loc['1980-03-31':'1989-12-31']
        nq=t.index.size
        print('Average for 1980s :', round(np.log(t[-1]/t[0])/(nq/4),4))  

        t=ser.loc['1990-03-31':'1999-12-31']
        nq=t.index.size
        print('Average for 1990s :', round(np.log(t[-1]/t[0])/(nq/4),4))

        t=ser.loc['2000-03-31':'2009-12-31']
        nq=t.index.size
        print('Average for 2000s :', round(np.log(t[-1]/t[0])/(nq/4),4))

        t=ser.loc['2010-03-31':'2019-12-31']
        nq=t.index.size
        print('Average for 2010s :', round(np.log(t[-1]/t[0])/(nq/4),4))
    else:
        # 20-year growth
        t=ser.loc['1950-03-31':'1969-12-31']
        nq=t.index.size
        print('Average for 1950/60 :', round(np.log(t[-1]/t[0])/(nq/4),4))

        t=ser.loc['1970-03-31':'1999-12-31']
        nq=t.index.size
        print('Average for 1970/80 :', round(np.log(t[-1]/t[0])/(nq/4),4))

        t=ser.loc['2000-03-31':'2019-12-31']
        nq=t.index.size
        print('Average for 2000/10 :', round(np.log(t[-1]/t[0])/(nq/4),4))

def get_eurostat_country_data(series, country, sadj):
    # get all indicators in "series" for "country" with "sadj" (SA/NSA) seasonal adjustment. Assumes monthly
    # Note this currently only works for the unemployment dataset
    df = eurostat.get_data_df(series, flags=False) 
    # pick country and seasonal adjustment, reshape to have dates as columns
    df = df[(df['geo\\time']==country)  & (df['s_adj']==sadj)].drop(['unit', 's_adj', 'geo\\time'],axis=1).set_index('indic').T
    # reset index and sort
    df = df.set_index(pd.to_datetime(df.index,format="%YM%m")).sort_index()
    df.index.name='date'
    return df

def get_eurostat_allcountry_data(series, indic, sadj):
    # get all countries with indicator "indic" in "series" for "country" with "sadj" (SA/NSA) seasonal adjustment
    df = eurostat.get_data_df(series, flags=False) 
    # pick indic and seasonal adjustment, reshape to have dates as columns
    df = df[(df['indic']==indic)  & (df['s_adj']==sadj)].drop(['unit', 's_adj', 'indic'],axis=1).set_index('geo\\time').T
    # reset index and sort
    df = df.set_index(pd.to_datetime(df.index,format="%YM%m")).sort_index()
    df.index.name='date'
    return df

def get_eurostat_allcountry_hicp(series, coicop):
    # get HICP data for category coicop ('CP00' is headline) in all Eurostat countries
    df = eurostat.get_data_df(series, flags=False) 
    # pick country and seasonal adjustment, reshape to have dates as columns
    df = df[(df['coicop']==coicop) & (df['unit']=='I15')].drop(['unit', 'coicop'],axis=1).set_index('geo\\time').T
    # reset index and sort
    df = df.set_index(pd.to_datetime(df.index,format="%YM%m")).sort_index()
    df.index.name='date'
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
            #'HCCSDODNS':'debt',              # Households and Nonprofit Organizations; Consumer Credit [may want to change]
            'TTLHH': 'hh',                    # Total number of households
            'POP': 'pop',                     # Total population (starts 1952, from Census)
            #'TERMCBCCINTNS': 'rcc',          # Commercial Bank Interest Rate on Credit Card Plans [only from 1996]
            'GDPDEF': 'gdpdef',               # GDP deflator
            'PCE': 'pcemonthly',              # Monthly PCE  
            'PCEPI': 'pcedefl',               # PCE deflator, chain-type (DPCERD3Q086SBEA is quarterly)
            'PCEPILFE': 'pcedeflcore',            # PCE deflator chain-type less food and energy (so core)
            'DPCCRV1Q225SBEA': 'pce_infl',    # Inflation in PCE excluding food-energy chain-type
            'CPIAUCSL': 'cpi',                # Consumer price index all urban
            'CPILFESL': 'cpicore',           # CPI less food and energy all urban (core CPI)
            #'M1SL': 'm1',                    # M1 money stock
            #'M2SL': 'm2',                    # M2 money stock 
            #'CURRCIR': 'currcir',            # Currency in circulation
            #'FEDFUNDS': 'fedfunds',           # Fed Funds rate
            'DFF': 'fedfunds',                # Effective Fed Funds rate
            'PAYEMS': 'emp',                  # All employee nonfarm, CES [150m] -- "Nonfarm payrolls"
            'PRS85006023': 'h',               # Avg weekly hours in nonfarm business, index 2012 (per person)
            'OPHNFB': 'labprod',              #  Output per hour of all persons (in nonfarm business sector)
            'PRS85006111':'ulc',              # Unit labor costs for all employed persions in the nonfarm business sector
            'PRS85006173':'laborshare',       # Labor share from the productivity relase 
            'COMPNFB': 'w',                   # Compensation per hour in nonfarm business (from productivity and costs, quarterly)
            'CES0500000003': 'w_ces',         # Average hourly earnings of all employees total private from the CES (monthly)
            'UNRATE': 'u',                    # Unemployment rate
            'EMRATIO': 'epop',                # Headline employment-pop ratio
            'CIVPART': 'partrate',            # Headline participation rate 
            'UNEMPLOY': 'ulevel',             # Unemployment level 
            'JTSJOL': 'jobopenings',          # Job openings: total nonfarm (JOLTS)
            'USREC': 'USREC',                 # NBER Recession indicator
            #'RKNANPUSA666NRUG':'k',          # Capital stock at constant prices (from Penn World tables)      
            #'NGDPPOT': 'ypotn',              # Nominal potential domestic product (CBO)
            #'GDPPOT': 'ypot',                # Real potential GDP
            #'TOTRESNS': 'totres',            # Total reserves of depository institutions
            #'IOER': 'ioer',                  # Interest rate on excess reserves (also equal to interest on required reserves)
            'DGS10':'dgs10',                  # 10 year treasury rate
            'T10YIE': 'breakeven10'}          # 10 year breakeven inflation rate 

    df = FredReader(series.keys(), start='1947').read().rename(series, axis='columns')

    # get rid of annoying double month stuff
    # assert (df.resample('M').count() <= 1).all().all()
    # df = df.resample('M').mean()

    # Adjust to freq 
    df = df.resample(freq).mean()

    if typedef=='same_def' and freq=='M':
        # interpolate the nominal series where we have available data for decomposition exercise
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
        #df['k'].interpolate(inplace=True)
        
    return df

