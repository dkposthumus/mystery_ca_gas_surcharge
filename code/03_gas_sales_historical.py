import requests
import pandas as pd
import json
from pathlib import Path

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 

# right now, my data for both gas sales and 
# gas tax per state only start in 2012 (sales) and 2013 (tax)
# however, for the DoT's data as such, historical data is only from PDFs
    # those pdfs are found here: https://www.fhwa.dot.gov/policyinformation/motorfuelhwy_trustfund.cfm
    # i converted pdf tables into csv files
gas_sales_historical_df = pd.DataFrame()
for year in range(2000, 2012):
    df = pd.read_csv(f'{raw_data}/gas_sales_historical/gas_sales_{year}.csv')
    df['year'] = year
    if 'DECEMBER TOTAL' in df.columns:
        df[['DECEMBER', 'TOTAL']] = df['DECEMBER TOTAL'].str.split(expand=True)
        df.drop(columns=['DECEMBER TOTAL'], inplace=True)
        df['DECEMBER'] = df['DECEMBER'].str.replace(',', '').astype(float)
        df['TOTAL'] = df['TOTAL'].str.replace(',', '').astype(float)
    if year in range(2000, 2002):
        df['state'] = df['STATE']
    df.drop(columns=['STATE', 'TOTAL'], inplace=True)
    df.rename(columns = {
        'Unnamed: 0': 'state',
        'JANUARY 2/': 'jan',
        'FEBRUARY 2/': 'feb',
        'MARCH 2/': 'mar',
        'APRIL 2/': 'apr',
        'MAY 2/': 'may', 
        'JUNE 2/': 'jun',
        'JULY 2/': 'jul',
        'AUGUST 2/': 'aug',
        'SEPTEMBER 2/': 'sept',
        'OCTOBER 2/': 'oct',
        'NOVEMBER 2/': 'nov',
        'DECEMBER 2/': 'dec',
        'JANUARY': 'jan',
        'FEBRUARY': 'feb',
        'MARCH': 'mar',
        'APRIL': 'apr',
        'MAY': 'may', 
        'JUNE': 'jun',
        'JULY': 'jul',
        'AUGUST': 'aug',
        'SEPTEMBER': 'sept',
        'OCTOBER': 'oct',
        'NOVEMBER': 'nov',
        'DECEMBER': 'dec',
    },
    inplace=True
    )
    gas_sales_historical_df = pd.concat([gas_sales_historical_df, df], ignore_index=True)
    #print(df.columns)
    # globals()[f'gas_sales_{year}_df'] = df
drop_states = ['U.S. Total', 'Puerto Rico', 'Grand Total', 'US Total']
gas_sales_historical_df = gas_sales_historical_df[~gas_sales_historical_df['state'].isin(drop_states)]

gas_sales_historical_df = pd.melt(gas_sales_historical_df, id_vars=['state', 'year'], 
                    var_name='month', value_name='value')
gas_sales_historical_df['day'] = 1
month_map = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
}
# Map the month abbreviations to their corresponding numbers
gas_sales_historical_df['month'] = gas_sales_historical_df['month'].map(month_map)
gas_sales_historical_df['date'] = pd.to_datetime(gas_sales_historical_df[['year', 'month', 'day']])
gas_sales_historical_df.drop(columns=['month', 'year', 'day'], inplace=True)
gas_sales_historical_df.to_csv(f'{data}/gas_historical.csv', index=False)