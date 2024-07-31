import requests
import pandas as pd
import json
from pathlib import Path
import numpy as np
# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 

# since we're NOT using an API for this data pull but a csv file, I'm defining where to find that csv file relative to the data macro set above
gas_tax_dot = f'{raw_data}/gas_tax_dot.csv'
# i'm going to do the same thing for the data on gasoline sales
gas_sales_dot = f'{raw_data}/gas_sales_dot.csv'
# now let's define only the variables we're interested in:
columns_to_keep = ['state', 'rate', 'MMFR_year', 'fuel_type']
# import the csv as a pandas dataframe -- including ONLY the columns we want
gas_tax_dot_df = pd.read_csv(gas_tax_dot, usecols=columns_to_keep)
# I am only interested in observations relating to GASOLINE -- not the other fuel types. so let's filter
gas_tax_dot_df = gas_tax_dot_df[gas_tax_dot_df['fuel_type'] == 'Gasoline']
# we no longer need the fuel_type variable, since they're all the same, i.e., Gasoline
gas_tax_dot_df = gas_tax_dot_df.drop(['fuel_type'], axis=1)
# now let's rename variables
gas_tax_dot_df = gas_tax_dot_df.rename(
    columns={'MMFR_year': 'date', 'rate': 'gas excise tax'}
)
# now let's format the dates as date
gas_tax_dot_df['date'] = pd.to_datetime(gas_tax_dot_df['date'], format='%Y')
gas_tax_historical_df = pd.read_csv(f'{data}/gas_tax_historical.csv')
gas_tax_dot_df = pd.concat([gas_tax_dot_df, gas_tax_historical_df], ignore_index=True)
gas_tax_dot_df['gas excise tax'] = pd.to_numeric(gas_tax_dot_df['gas excise tax'], errors='coerce')
gas_tax_dot_df['gas excise tax'] = gas_tax_dot_df['gas excise tax'].multiply(0.01)
gas_tax_dot_df['date'] = pd.to_datetime(gas_tax_dot_df['date'])

# let's check the data
print(gas_sales_dot_df)
print(gas_tax_dot_df)
# now merge the sales and tax data on date as well as state to create a large panel data
gas_sales_tax_dot_df = pd.merge(
    gas_tax_dot_df, gas_sales_dot_df, on=['state', 'date'], how='outer'
)
gas_sales_tax_dot_df['value'] = pd.to_numeric(gas_sales_tax_dot_df['value'], errors='coerce')

gas_sales_tax_dot_df.to_csv(f'{data}/test.csv', index=False)

# now let's create a weighted average the sales tax for the states EXCEPT California
# drop observations relating to the US total gasoline sold, the federal tax, and California
states_to_remove = ['US Total', 'Federal Tax', 'California']
# Filter the DataFrame to exclude rows where 'state' is in states_to_remove
avg_gas_state_tax_df = gas_sales_tax_dot_df[~gas_sales_tax_dot_df['state'].isin(states_to_remove)]
    # I need to forward fill the tax data so that there are no missings
    # this ensures that every month from a year has a constant tax rate
    # let's do the same thing for the values of gas sales, ensuring that our weighted average below isn't distorted
for var in ['gas excise tax']:
    avg_gas_state_tax_df[var] = avg_gas_state_tax_df.groupby('state')[var].fillna(
        method='ffill'
    )
avg_gas_state_tax_df = avg_gas_state_tax_df.dropna(subset=['value'])
# now I'm going to calculate the average tax rate for all states, grouped by date and weighted by their gasoline sold
avg_gas_state_tax_df = avg_gas_state_tax_df.groupby('date').apply(
    lambda x: (x['gas excise tax'] * x['value']).sum() / x['value'].sum()
)
# reset index
avg_gas_state_tax_df = avg_gas_state_tax_df.reset_index(
    name='average state tax excl. ca'
)
print(avg_gas_state_tax_df)

# I need a separate dataset, one consisting of only the national total and California's total
# I filter these states' data from the gas sales DOT dataframe above
states_of_interest = ['US Total', 'California']
gas_sales_dot_filtered_df = gas_sales_dot_df[
    gas_sales_dot_df['state'].isin(states_of_interest)
]
# now let's pull just the variable for california's share of US sold gasoline using the same spreadsheet
# start by reshaping so that the total US and CA figures are different
# here I'm making the total US and California each their own column for manipulation, so date is index
gas_sales_dot_filtered_df = gas_sales_dot_filtered_df.pivot_table(
    index='date', columns='state', values='value', fill_value=None
)
gas_sales_dot_filtered_df = gas_sales_dot_filtered_df.reset_index()
# now let's rename for consistency/ease of understanding
gas_sales_dot_filtered_df = gas_sales_dot_filtered_df.rename(
    columns={'California': 'ca total gas sold', 'US Total': 'usa total gas sold'}
)
# generate a variable demonstrating the share of gas sold in the country sold in california
gas_sales_dot_filtered_df['ca share of usa gas'] = (
    gas_sales_dot_filtered_df['ca total gas sold']
    / gas_sales_dot_filtered_df['usa total gas sold']
)
# this variable is missing for some dates; thus, for those dates where it is missing only i will be replacing it with 0.1, borrowing severin's assumption
gas_sales_dot_filtered_df['ca share of usa gas'].fillna(0.1, inplace=True)
print(gas_sales_dot_filtered_df)

# now let's focus on pulling, together, 1) california's tax rate and the federal tax rate
states_of_interest = ['Federal Tax']
# filter the tax dataset so that it ONLY includes california state and federal tax rates
gas_fed_tax_df = gas_tax_dot_df[gas_tax_dot_df['state'].isin(states_of_interest)]
gas_fed_tax_df = gas_fed_tax_df.pivot_table(
    index='date', columns='state', values='gas excise tax', fill_value=None
)
# rename appropriately
gas_fed_tax_df = gas_fed_tax_df.rename(
    columns={'Federal Tax': 'federal gas tax'}
)
print(gas_fed_tax_df)
# now hard-code california excise tax rate
ca_tax = {
    'date': [
        '07/01/2024',
        '07/01/2023',
        '07/01/2022',
        '07/01/2021',
        '07/01/2020',
        '07/01/2019',
        '07/01/2018',
        '11/01/2017',
        '07/01/2017',
        '07/01/2016',
        '07/01/2015',
        '04/01/2015',
        '07/01/2014',
        '07/01/2013',
        '07/01/2012',
        '04/01/2012',
        '07/01/2011',
        '04/01/2011',
        '07/01/2010',
        '04/01/2010',
    ],
    'ca state gas tax': [
        0.596,
        0.579,
        0.539,
        0.511,
        0.505,
        0.473,
        0.417,
        0.417,
        0.297,
        0.278,
        0.300,
        0.360,
        0.360,
        0.395,
        0.360,
        0.357,
        0.357,
        0.353,
        0.353,
        0.180,
    ]
}
ca_tax_df = pd.DataFrame(ca_tax)
ca_tax_df['date'] = pd.to_datetime(ca_tax_df['date'])
# now merge four datasets together
gas_tax_df = pd.merge(gas_sales_dot_filtered_df, avg_gas_state_tax_df, on='date', how='outer')
gas_tax_df = pd.merge(gas_tax_df, ca_tax_df, on='date', how='outer')
gas_tax_df = pd.merge(gas_tax_df, gas_fed_tax_df, on='date', how='outer')
# frontfill missing observations for the tax variables related to Ca and Federal tax
gas_tax_df[['ca state gas tax', 'federal gas tax']] = gas_tax_df[
    ['ca state gas tax', 'federal gas tax']
].fillna(method='ffill')
# let's check the dataset:
gas_tax_df.to_csv(f'{data}/gas_taxes.csv', index=False)
