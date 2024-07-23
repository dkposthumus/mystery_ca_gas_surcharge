import pandas as pd
from pathlib import Path
import numpy as np
import calendar

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 

# let's start by importing the cpi data as a pandas dataframe
cpi = pd.read_csv(f'{data}/cpi.csv')
# now let's import the retail gas prices
gas_retail_df = pd.read_csv(f'{data}/gas_retail.csv')
# spot gas prices
spot_prices_df = pd.read_csv(f'{data}/spot_prices.csv')
# tax data
gas_taxes_df = pd.read_csv(f'{data}/gas_taxes.csv')
# LCFS data 
lcfs_df = pd.read_csv(f'{data}/lcfs.csv')
# UST data 
ust_df = pd.read_csv(f'{data}/ust.csv')
# CAX data
cax_df = pd.read_csv(f'{data}/cax.csv')
# let's merge on date for each of the 4 datasets of interest:
master_df = pd.merge(cpi, gas_retail_df, on='date', how='outer')
master_df = pd.merge(master_df, spot_prices_df, on='date', how='outer')
master_df = pd.merge(master_df, gas_taxes_df, on='date', how='outer')
master_df = pd.merge(master_df, lcfs_df, on='date',how='outer')
master_df = pd.merge(master_df, ust_df, on='date',how='outer')
master_df = pd.merge(master_df, cax_df, on='date',how='outer')
# now i need to forward fill some variables since they're currently only non-missing for the first day of its duration
for ffill_var in ['ust fee', 'cax cost']:
    master_df[ffill_var] = master_df[ffill_var].fillna(
    method='ffill'
)
master_df['date'] = pd.to_datetime(master_df['date'])

# Set 'Date' as index
master_df.set_index('date', inplace=True)

master_df.to_csv(f'{data}/master.csv', index=True)