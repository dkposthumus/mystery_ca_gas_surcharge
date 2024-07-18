import pandas as pd
import matplotlib.pyplot as plt

data_path = '/Users/danpost/Dropbox/Myster_Gas_Surcharge/Analysis/Data'
# let's start by importing the cpi data as a pandas dataframe
cpi = pd.read_csv(f'{data_path}/cpi.csv')
# now let's import the retail gas prices
gas_retail_df = pd.read_csv(f'{data_path}/gas_retail.csv')
# spot gas prices
spot_prices_df = pd.read_csv(f'{data_path}/spot_prices.csv')
# tax date
gas_taxes_df = pd.read_csv(f'{data_path}/gas_taxes.csv')
# let's merge on date for each of the 4 datasets of interest:
master_df = pd.merge(cpi, gas_retail_df, on='date', how='outer')
master_df = pd.merge(master_df, spot_prices_df, on='date', how='outer')
master_df = pd.merge(master_df, gas_taxes_df, on='date', how='outer')
master_df['date'] = pd.to_datetime(master_df['date'])

# Set 'Date' as index
master_df.set_index('date', inplace=True)

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
fixed_cpi = master_df.loc['03/01/2017', 'all-urban cpi']
master_df['price deflator'] = master_df['all-urban cpi'] / fixed_cpi

# Severin assumes that local taxes outside of CA average to 1%, so let's find that cost per gallon
master_df['average ca local tax'] = (
    0.01 * master_df['california gas (retail) (nominal)']
)

# now i want to create a total taxes and fees variable for california
master_df['ca total fees and taxes'] = (
    master_df['ca state gas tax'] + master_df['average ca local tax']
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
master_df.to_csv(f'{data_path}/master.csv', index=True)
