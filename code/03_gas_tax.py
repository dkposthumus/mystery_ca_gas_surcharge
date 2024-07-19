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
# right now, the values are in cents/gallon; we want to make it dollars/gallon, so multiply by 0.01 (same as dividing by 100)
gas_tax_dot_df['gas excise tax'] = gas_tax_dot_df['gas excise tax'].multiply(0.01)
# now let's format the dates as date
gas_tax_dot_df['date'] = pd.to_datetime(gas_tax_dot_df['date'], format='%Y')

# now i want to import as a csv of state-by-state historical data on retail gasoline sales, which ill use to find the number of gallons sold in california relative to the US
# first let's define the list of columns that i'm actually interested in importing
columns_to_keep = ['state', 'value', 'date', 'fuel_type']
# now let's import the csv, including only the columns listed above that are necessary
gas_sales_dot_df = pd.read_csv(gas_sales_dot, usecols=columns_to_keep)
# I am only interested in GASOLINE, not the special fuels -- so let's keep only the gasoline observations
gas_sales_dot_df = gas_sales_dot_df[gas_sales_dot_df['fuel_type'] == 'Gasoline/gasohol']
# now the fuel_type variable is no longer needed, as all observations are gasoline
gas_sales_dot_df.drop(columns=['fuel_type'], inplace=True)
# format date as a true date variable
gas_sales_dot_df['date'] = pd.to_datetime(
    gas_sales_dot_df['date'], format='%m/%d/%y %H:%M'
)
# let's check the data
print(gas_sales_dot_df)
print(gas_tax_dot_df)
# now merge the sales and tax data on date as well as state to create a large panel data
gas_sales_tax_dot_df = pd.merge(
    gas_tax_dot_df, gas_sales_dot_df, on=['state', 'date'], how='outer'
)
print(gas_sales_tax_dot_df)

# now let's create a weighted average the sales tax for the states EXCEPT California
# drop observations relating to the US total gasoline sold, the federal tax, and California
for group in ['US Total', 'Federal Tax', 'California']:
    avg_gas_state_tax_df = gas_sales_tax_dot_df[gas_sales_tax_dot_df['state'] != group]
    # I need to forward fill the tax data so that there are no missings
    # this ensures that every month from a year has a constant tax rate
avg_gas_state_tax_df['gas excise tax'] = avg_gas_state_tax_df['gas excise tax'].fillna(
    method='ffill'
)
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
print(gas_sales_dot_filtered_df)

# now let's focus on pulling, together, 1) california's tax rate and the federal tax rate
states_of_interest = ['Federal Tax', 'California']
# filter the tax dataset so that it ONLY includes california state and federal tax rates
gas_fed_ca_tax_df = gas_tax_dot_df[gas_tax_dot_df['state'].isin(states_of_interest)]
gas_fed_ca_tax_df = gas_fed_ca_tax_df.pivot_table(
    index='date', columns='state', values='gas excise tax', fill_value=None
)
# rename appropriately
gas_fed_ca_tax_df = gas_fed_ca_tax_df.rename(
    columns={'California': 'ca state gas tax', 'Federal Tax': 'federal gas tax'}
)
print(gas_fed_ca_tax_df)
# now merge four datasets together
gas_tax_df = pd.merge(
    gas_sales_dot_filtered_df, avg_gas_state_tax_df, on='date', how='outer'
)
gas_tax_df = pd.merge(gas_tax_df, gas_fed_ca_tax_df, on='date', how='outer')
# backfill missing observations for the tax variables related to Ca and Federal tax
gas_tax_df[['ca state gas tax', 'federal gas tax']] = gas_tax_df[
    ['ca state gas tax', 'federal gas tax']
].fillna(method='ffill')
# let's check the dataset:
print(gas_tax_df)
gas_tax_df.to_csv(f'{data}/gas_taxes.csv', index=False)
