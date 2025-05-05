import pandas as pd
from pathlib import Path
import numpy as np
import calendar

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge' / 'washington_state')
data = (work_dir / 'data')
clean_data = (data / 'clean')
code = Path.cwd() 

# let's start by importing the cpi data as a pandas dataframe
cpi = pd.read_csv(f'{clean_data}/cpi.csv')
# now let's import the retail gas prices
gas_retail_df = pd.read_csv(f'{clean_data}/gas_retail.csv')
# tax data
gas_taxes_df = pd.read_csv(f'{clean_data}/gas_taxes.csv')
# cap and invest cost 
cax = pd.read_csv(f'{clean_data}/cax.csv')
'''# special district tax 
special_district_tax_df = pd.read_excel(f'{raw_data}/special_district_sales_tax.xlsx', header = 1)
special_district_tax_df['date'] = pd.to_datetime(special_district_tax_df['MonthYear'])
special_district_tax_df.drop(columns={'MonthYear'}, inplace=True)'''
# let's merge on date for each of the 4 datasets of interest:
master_df = pd.merge(cpi, gas_retail_df, on='date', how='outer')
master_df = pd.merge(master_df, gas_taxes_df, on='date', how='outer')
master_df = pd.merge(master_df, cax, on='date', how='outer')

master_df['date'] = pd.to_datetime(master_df['date'])

'''master_df = pd.merge(master_df, special_district_tax_df, on='date', how='outer')'''
# now i need to forward fill some variables since they're currently only non-missing for the first day of its duration
vars_ffill = ['ust fee', 'cax cost', 'all-urban cpi', 'special district sales tax', 
            'california gas (retail) (nominal)', 'national gas (retail) (nominal)', 
            'la spot price (nominal)',
            'ny spot price (nominal)', 'gulf spot price (nominal)', 'uk brent (nominal)',
            'ca state gas sales tax rate', 'ca state gas tax','ca total gas sold', 
            'ca share of usa gas', 'average state tax excl. ca', 'lcfs credit price', 'lcfs cost',
            'padd5 crude refiner acquisition cost (nominal)']
vars_ffill = [
    'all-urban cpi', 'washington gas (retail) (nominal)', 'national gas (retail) (nominal)',
    'wa excise tax', 'wa total gas sold', 'wa share of usa gas', 'average state tax excl. wa', 
    'cax cost'
]
for ffill_var in vars_ffill:
    master_df[ffill_var] = master_df[ffill_var].fillna(
    method='ffill'
)
    
# now for those vars_ffill, fill in missing observations of 'cax cost' with 0s
master_df['cax cost'] = master_df['cax cost'].fillna(0)

# Set 'Date' as index
master_df.set_index('date', inplace=True)
# make sure that date variable is datetime
master_df.index = pd.to_datetime(master_df.index)

# next I need to calculate a separate variable, a national retail price average EXCLUDING california
# for this step, I am incorporating CA's share of national gasoline sold (in gallons)
# this is an empirical improvement on Severin's assumption that CA accounts for 10% of national gasoline sold
master_df['national retail excl. wa (nominal)'] = (
    master_df['national gas (retail) (nominal)']
    - (
        master_df['wa share of usa gas']
        * master_df['washington gas (retail) (nominal)']
    )
) / (1 - master_df['wa share of usa gas'])

# there are some CA-specific costs for which I want to replace missing observations with 0, 
# since a missing observations indicates that program didn't exist and thus the associated cost was 0
upper_bound_date = pd.to_datetime('2016-01-01')
# Fill NaN values with 0 up to the specified upper bound date for a given variable
mask = master_df.index <= upper_bound_date
# Apply fillna only to the subset of data within the date range
'''for var in ['ust fee', 'cax cost', 'lcfs cost']:
    master_df.loc[mask, var] = master_df.loc[mask, var].fillna(0)'''

# now i want to convert the NOMINAL prices into REAL prices
# let's fix the march 2017 observation of CPI as our baseline and make a price deflator variable
# Severin anchors CPI to the same month/year
cpi_anchor = pd.to_datetime('2023-03-01')
fixed_cpi = master_df.loc[cpi_anchor, 'all-urban cpi']
master_df['price deflator'] = master_df['all-urban cpi'] / fixed_cpi

# now multiply by california's nominal retail gas price to find the cost per gallon, INCLUSIVE of the gas tax
'''master_df['ca state.local tax rate'] = master_df['ca state gas sales tax rate'] + master_df['special district sales tax']
master_df['ca state.local tax cost'] = (master_df['ca state.local tax rate']/(master_df['ca state.local tax rate']+1))*master_df['california gas (retail) (nominal)']
'''
# now i want to create a total taxes and fees variable for california
master_df['wa total fees and taxes'] = (
    master_df['wa excise tax'] 
    + master_df['cax cost']
)

# let's now calculate the mystery gas surcharge
master_df['unexplained differential (nominal)'] = (
    master_df['washington gas (retail) (nominal)']
    - master_df['wa total fees and taxes']
) - (
    master_df['national retail excl. wa (nominal)']
    - master_df['average state tax excl. wa']
)

# the explained differential will be the difference between california and national gas prices, w/ the unexplained differential subtracted:
master_df['explained differential (nominal)'] = (
    master_df['washington gas (retail) (nominal)']
    - master_df['national retail excl. wa (nominal)']
) - master_df['unexplained differential (nominal)']

# now let's run through a loop applying this to all our price variables
prices = [
    'unexplained differential',
    'explained differential',
]
for var in prices:
    master_df[f'{var} (real)'] = (
        master_df[f'{var} (nominal)'] / master_df['price deflator']
    )

# let's find the annual average, grouping by year
master_df['year'] = master_df.index.year

# for the next daily calculation i need a variable capturing the number of days in each month
master_df['month'] = master_df.index.month
def days_in_month(year, month):
    return calendar.monthrange(int(year), int(month))[1]
# Apply the function to create the 'days in month' variable
master_df['days in month'] = master_df.apply(lambda row: days_in_month(row['year'], row['month']), axis=1)

# I want to find the total cost per month paid by california drivers
    # this formula is simply the total gas sold in california monthly x the unexplained differential
    # note: i'm using the REAL unexplained differential
master_df['monthly cost of surcharge (millions)'] = (master_df['unexplained differential (real)']
                                        *master_df['wa total gas sold'])/1000000
# now let's find the average per day, using the 12-month moving average divided by 30.5
# now divide that moving average by 30.5 and multiply by unexplained differential to find the daily average cost
master_df['average daily cost of mgs (millions)'] = ((master_df['wa total gas sold']
                                        /master_df['days in month'])*master_df['unexplained differential (real)'])/1000000

# next i want to calculate a variable that severin refers to as CA Margin, 
# which is the retail price of CA gas minus the crude price and fees/taxes in CA
#master_df['wa margin (real)'] = (master_df['washington gas (retail) (nominal)'] - (master_df['padd5 crude refiner acquisition cost (nominal)']) - master_df['wa excise tax'])/master_df['price deflator']

'''# now let's calculate the difference between an average of the new york and gulf spot prices and LA spot price:
master_df['spot price differential (real)'] = (master_df['la spot price (nominal)'] - ((master_df['gulf spot price (nominal)']+master_df['ny spot price (nominal)'])/2))/master_df['price deflator']

master_df['mgs - spot price differential (real)'] = master_df['unexplained differential (real)'] - master_df['spot price differential (real)']'''

master_df.to_csv(f'{clean_data}/master.csv', index=True)

# now let's create a csv with ONLY the unexplained differential (real) column 
master_df = master_df[['unexplained differential (real)']]
master_df.rename(
    columns = {'unexplained differential (real)': 'wa_mgs_real'}, inplace=True
)
master_df.to_csv(f'{clean_data}/wa_mgs_real.csv', index=True)