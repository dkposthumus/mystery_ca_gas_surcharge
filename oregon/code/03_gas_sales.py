import requests
import pandas as pd
import json
from pathlib import Path

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge-1' / 'oregon')
data = (work_dir / 'data')
raw_data_sales = (home_dir / 'mystery_ca_gas_surcharge-1' / 'california' / 'data' / 'raw')
clean_data = (data / 'clean')
code = Path.cwd() 

# right now, my data for both gas sales and 
# gas tax per state only start in 2012 (sales) and 2013 (tax)
# however, for the DoT's data as such, historical data is only from PDFs
    # those pdfs are found here: https://www.fhwa.dot.gov/policyinformation/motorfuelhwy_trustfund.cfm
    # i converted pdf tables into csv files
gas_sales_historical_df = pd.DataFrame()
for year in range(2000, 2012):
    df = pd.read_csv(f'{raw_data_sales}/gas_sales_historical/gas_sales_{year}.csv')
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
# now rename U.S Total observations to US Total to match the DoT data
gas_sales_historical_df['state'] = gas_sales_historical_df['state'].replace('U.S. Total', 'US Total')
gas_sales_historical_df = pd.melt(gas_sales_historical_df, id_vars=['state', 'year'], 
                    var_name='month', value_name='value')
gas_sales_historical_df['day'] = 1
month_map = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12
}
# Map the month abbreviations to their corresponding numbers
gas_sales_historical_df['month'] = gas_sales_historical_df['month'].map(month_map)
gas_sales_historical_df['date'] = pd.to_datetime(gas_sales_historical_df[['year', 'month', 'day']])
gas_sales_historical_df.drop(columns=['month', 'year', 'day'], inplace=True)

# first let's define the list of columns that i'm actually interested in importing
columns_to_keep = ['state', 'value', 'date', 'fuel_type']
# now let's import the csv, including only the columns listed above that are necessary
gas_sales_dot_df = pd.read_csv(f'{raw_data_sales}/gas_sales_dot.csv', usecols=columns_to_keep)
# I am only interested in GASOLINE, not the special fuels -- so let's keep only the gasoline observations
gas_sales_dot_df = gas_sales_dot_df[gas_sales_dot_df['fuel_type'] == 'Gasoline/gasohol']
# now the fuel_type variable is no longer needed, as all observations are gasoline
gas_sales_dot_df.drop(columns=['fuel_type'], inplace=True)
# format date as a true date variable
gas_sales_dot_df['date'] = pd.to_datetime(
    gas_sales_dot_df['date'], format='%m/%d/%y %H:%M'
)
gas_sales_df = pd.concat([gas_sales_dot_df, gas_sales_historical_df], ignore_index=True)
gas_sales_df.rename(columns={'value': 'gasoline sales'}, inplace=True)
drop_states = ['Puerto Rico', 'Grand Total']
gas_sales_df = gas_sales_df[~gas_sales_df['state'].isin(drop_states)]
gas_sales_df['state'] = gas_sales_df['state'].replace(
    {'District of Columbia': 'DC', 'Dist. of Col.': 'DC'}
)
# now we have to destring the gasoline sales variable
gas_sales_df['gasoline sales'] = pd.to_numeric(gas_sales_df['gasoline sales'].replace({',': ''}, regex=True), errors='coerce')
gas_sales_df.to_csv(f'{clean_data}/gas_sales.csv', index=False)