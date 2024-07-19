import pandas as pd
from pathlib import Path
import numpy as np

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

# Severin assumes that the NOMINAL cost premium to produce CA's cleaner-burning gasoline blend is CONSTANT, at 10 cents 
master_df['carb cost premium'] = 0.1

# next I need to calculate a separate variable, a national retail price average EXCLUDING california
# for this step, I am incorporating CA's share of national gasoline sold (in gallons)
# this is an empirical improvement on Severin's assumption that CA accounts for 10% of national gasoline sold
master_df['national retail excl. ca (nominal)'] = (
    master_df['national gas (retail) (nominal)']
    - (
        master_df['ca share of usa gas']
        * master_df['california gas (retail) (nominal)']
    )
) / (1 - master_df['ca share of usa gas'])

# now i want to convert the NOMINAL prices into REAL prices
# let's fix the march 2017 observation of CPI as our baseline and make a price deflator variable
# Severin anchors CPI to the same month/year
fixed_cpi = master_df.loc['10/01/2023', 'all-urban cpi']
master_df['price deflator'] = master_df['all-urban cpi'] / fixed_cpi

# CA state sales tax on gas -- separate from the excise tax -- has been fixed at 2.25% since 03/01/2011. We can add the assum 1% local sales tax and input a constant 3.25% variable, beginning with 03/01/2011
master_df['ca state.local tax rate'] = np.nan
master_df.loc[master_df.index == '2011-03-01', 'ca state.local tax rate'] = 0.0325
# now let's front fill that variable 
master_df['ca state.local tax rate'] = master_df['ca state.local tax rate'].fillna(method='ffill')
# now multiply by california's nominal retail gas price to find the cost per gallon
master_df['ca state.local tax cost'] = master_df['california gas (retail) (nominal)']*master_df['ca state.local tax rate']

# now i want to create a total taxes and fees variable for california
master_df['ca total fees and taxes'] = (
    master_df['ca state gas tax'] 
    + master_df['ca state.local tax cost']
    + master_df['lcfs cost']
    + master_df['ust fee']
    + master_df['carb cost premium']
    + master_df['cax cost']
)

# let's now calculate the mystery gas surcharge
master_df['unexplained differential (nominal)'] = (
    master_df['california gas (retail) (nominal)']
    - master_df['ca total fees and taxes']
) - (
    master_df['national retail excl. ca (nominal)']
    - master_df['average state tax excl. ca']
)

# the explained differential will be the difference between california and national gas prices, w/ the unexplained differential subtracted:
master_df['explained differential (nominal)'] = (
    master_df['california gas (retail) (nominal)']
    - master_df['national retail excl. ca (nominal)']
) - master_df['unexplained differential (nominal)']

# now let's run through a loop applying this to all our price variables
prices = [
    'california gas (retail)',
    'national gas (retail)',
    'national retail excl. ca',
    'gulf spot price',
    'ny spot price',
    'la spot price',
    'uk brent',
    'unexplained differential',
    'explained differential',
]
for var in prices:
    master_df[f'{var} (real)'] = (
        master_df[f'{var} (nominal)'] / master_df['price deflator']
    )

# let's save the master data as a csv
master_df.to_csv(f'{data}/master.csv', index=True)
