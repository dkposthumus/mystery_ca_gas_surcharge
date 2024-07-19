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

# so the UST is historic data; since the fee is constant for many years, I'll simply hard code the observations 
    # here is the datasource (same as the one used by Severin): https://www.cdtfa.ca.gov/taxes-and-fees/tax-rates-stfd.htm, under "Underground Storage Tank Maintenance Fee"
ust = {
    'date': [
        '01/01/2015',
        '01/01/2014',
        '01/01/2010',
        '01/01/2006',
        '01/01/2005',
        '01/01/1997',
        '01/01/1996',
        '01/01/1995',
        '01/01/1991',
    ],
    'ust fee': [
        0.020,
        0.014,
        0.020,
        0.014,
        0.013,
        0.012,
        0.009,
        0.007,
        0.006,
    ]
}
# Creating DataFrame
ust_df = pd.DataFrame(ust)
# now I want to make the date variable a pandas datetime formatted variable:
ust_df['date'] = pd.to_datetime(ust_df['date'])
# check the dataframe 
print(ust_df)
ust_df.to_csv(f'{data}/ust.csv', index=False)