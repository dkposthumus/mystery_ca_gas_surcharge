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

# import the severin data 
severin = f'{raw_data}/severin.csv'
severin_df = pd.read_csv(severin)
# for the sake of comparison, I am only interested in some of the variables in the severin spreadsheet -- filter accordingly
cols_keep = [
    'YEAR', 'Month', 'US price without CA', 
    'TOT CA TAXES AND FEES', 'CA cap and trade cost (CAX)', 'LCFS',
    'Unexplained Differential', 'Explained Differential', 
    'Quantity', 'Annual Average Daily Usage', 'Extra Payment',
    'REAL ($current month) Unexplained Differential',
    'CA Regular All Formulations Retail Gasoline Prices (Dollars per Gallon)',
    'US state excise tax without CA',
    'CA UST', 'CA STATE EXCISE GASOLINE', 'TOT CA GAS TAXES',
    'Quantity', 'REAL ($current month) Extra Payment in $mil',
    'Daily Excess Payment (millions)',
]
severin_df = severin_df[cols_keep]
# now i want to rename all these variables:
severin_df = severin_df.rename(
    columns={
        'YEAR' : 'year',
        'Month' : 'month',
        'US price without CA' : 'national retail excl. ca (nominal) (severin)',
        'TOT CA TAXES AND FEES' : 'ca total fees and taxes (severin)', 
        'CA cap and trade cost (CAX)' : 'cax cost (severin)', 
        'LCFS' : 'lcfs cost (severin)',
        'Unexplained Differential' : 'unexplained differential (nominal) (severin)', 
        'Explained Differential' : 'explained differential (nominal) (severin)', 
        'Quantity' : 'quantity gas sold (severin)', 
        'Annual Average Daily Usage' : 'annual average daily usage (severin)', 
        'Extra Payment' : 'extra payment (severin)',
        'REAL ($current month) Unexplained Differential' : 'unexplained differential (real) (severin)',
        'CA Regular All Formulations Retail Gasoline Prices (Dollars per Gallon)' : 'california gas (retail) (nominal) (severin)',
        'US state excise tax without CA' : 'average state tax excl. ca (severin)',
        'CA UST' : 'ust fee (severin)', 
        'CA STATE EXCISE GASOLINE' : 'ca state gas tax (severin)',
        'TOT CA GAS TAXES': 'ca state.local tax cost (severin)',
        'Quantity': 'ca total gas sold (severin)',
        'REAL ($current month) Extra Payment in $mil': 'monthly cost of surcharge (millions) (severin)',
        'Daily Excess Payment (millions)': 'average daily cost of mgs (millions) (severin)'
    }
)
# let's make a proper date variable
severin_df['day'] = 1
severin_df['date'] = pd.to_datetime(severin_df[['year', 'month', 'day']])
# drop day, year, month variables
severin_df = severin_df.drop(columns=['year', 'month', 'day'])

severin_df.to_csv(f'{data}/severin.csv', index=False)