import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge-1' / 'nevada')
data = (work_dir / 'data')
raw_data_taxes = (home_dir / 'mystery_ca_gas_surcharge-1' / 'california' / 'data' / 'raw')
clean_data = (data / 'clean')
code = Path.cwd() 

gas_tax_historical_df = pd.read_csv(f'{raw_data_taxes}/gas_tax_historical/historical_gas_tax_2013.csv')
# define the types of observations we're NOT interested in (note: this is because the federal tax is constant)
drop_states = ['Mean', 'Weighted Avg', 'Puerto Rico', 'Federal Tax']
gas_tax_historical_df = gas_tax_historical_df[~gas_tax_historical_df['State'].isin(drop_states)]
gas_tax_historical_df['GasolineEffDate'] = pd.to_datetime(gas_tax_historical_df['GasolineEffDate'])
gas_tax_historical_df.loc[gas_tax_historical_df['GasolineEffDate'] == '2071-07-01', 'GasolineEffDate'] = pd.to_datetime('1971-07-01')
# now i want to find and store a list of states whose effective date is before january 01, 2000
cutoff_date = pd.to_datetime('2000-01-01')
filtered_df = gas_tax_historical_df[gas_tax_historical_df['GasolineEffDate'] < cutoff_date]
states_list = filtered_df['State'].unique().tolist()
# okay so basically i don't need to worry about these variables any longer
# let's pull our next dataset
gas_tax_historical = pd.DataFrame()
for year in range(2001, 2012):
    df = pd.read_csv(f'{raw_data_taxes}/gas_tax_historical/historical_gas_tax_{year}.csv')
    df.columns = ['State', 'GasolineRate', 'GasolineEffDate']
    df = df[~df['State'].isin(states_list)]
    df['State'] = df['State'].str.replace(' \*', '', regex=True)
    print(df['State'].unique())
    df['State'] = df['State'].fillna(method='ffill')
    df['GasolineEffDate'] = pd.to_datetime(df['GasolineEffDate'])
    gas_tax_historical = pd.concat([gas_tax_historical, df], ignore_index=True)

gas_tax_historical_df = pd.concat([gas_tax_historical_df, gas_tax_historical], ignore_index=True)
gas_tax_historical_df = gas_tax_historical_df.drop_duplicates()
gas_tax_historical_df = gas_tax_historical_df.dropna(subset=['GasolineEffDate'])
gas_tax_historical_df.rename(columns = {
        'GasolineEffDate': 'date',
        'GasolineRate': 'gas excise tax',
        'State': 'state'
    },
    inplace=True
    )
gas_tax_historical_df.loc[gas_tax_historical_df['date'] == '2061-07-01', 'date'] = pd.to_datetime('1961-07-01')
gas_tax_dot = f'{raw_data_taxes}/gas_tax_dot.csv'
# i'm going to do the same thing for the data on gasoline sales
gas_sales_dot = f'{raw_data_taxes}/gas_sales_dot.csv'
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
gas_tax_df = pd.concat([gas_tax_dot_df, gas_tax_historical_df], ignore_index=True)
# this dataset poses several challenges
    # first, some of these gas taxes are old
        # Georgia, for example, has had it's 7.5 cents gas tax since 1971 
        # I'm not worrying about these right now; the gas tax variable will be front-filled when merged onto 
        # the gas sales dataset
gas_tax_df['state'] = gas_tax_df['state'].replace(
    {'District of Columbia': 'DC', 'Dist. of Col.': 'DC'}
)
gas_tax_df['gas excise tax'] = pd.to_numeric(gas_tax_df['gas excise tax'], errors='coerce')
gas_tax_df['gas excise tax'] = gas_tax_df['gas excise tax']*0.01
gas_sales_df = pd.read_csv(f'{clean_data}/gas_sales.csv')
gas_sales_df['date'] = pd.to_datetime(gas_sales_df['date'])
gas_tax_df = pd.merge(gas_tax_df, gas_sales_df, on=['date','state'], how='outer')
gas_tax_df = gas_tax_df.sort_values(by=['state', 'date'])

gas_tax_df['gas excise tax'] = gas_tax_df['gas excise tax'].fillna(method='ffill')

wa_excise_df = gas_tax_df[gas_tax_df['state'] == 'Nevada']
wa_excise_df.rename(
    columns = {
        'gas excise tax': 'nv excise tax'
    }, inplace=True
)
wa_excise_df = wa_excise_df[['nv excise tax', 'date']]

states_to_remove = ['US Total', 'Federal Tax', 'Nevada']
# Filter the DataFrame to exclude rows where 'state' is in states_to_remove
avg_gas_state_tax_df = gas_tax_df[~gas_tax_df['state'].isin(states_to_remove)]
avg_gas_state_tax_df = avg_gas_state_tax_df.groupby('date').apply(
    lambda x: (x['gas excise tax'] * x['gasoline sales']).sum() / x['gasoline sales'].sum()
)
# reset index
avg_gas_state_tax_df = avg_gas_state_tax_df.reset_index(
    name='average state tax excl. nv'
)

# the next thing we need is California's share of the us total gasoline sold
states_of_interest = ['US Total', 'Nevada']
nv_share_usa_total = gas_sales_df[
    gas_sales_df['state'].isin(states_of_interest)
]
# now let's pull just the variable for california's share of US sold gasoline using the same spreadsheet
# start by reshaping so that the total US and CA figures are different
# here I'm making the total US and California each their own column for manipulation, so date is index
nv_share_usa_total = nv_share_usa_total.pivot_table(
    index='date', columns='state', values='gasoline sales', fill_value=None
)
nv_share_usa_total = nv_share_usa_total.reset_index()
nv_share_usa_total = nv_share_usa_total.rename(
    columns={'Nevada': 'nv total gas sold', 'US Total': 'usa total gas sold'}
)
# generate a variable demonstrating the share of gas sold in the country sold in california
nv_share_usa_total['nv share of usa gas'] = (
    nv_share_usa_total['nv total gas sold']
    / nv_share_usa_total['usa total gas sold']
)
# this variable is missing for some dates; thus, for those dates where it is missing only i will be replacing it with 0.1, borrowing severin's assumption
nv_share_usa_total['nv share of usa gas'].fillna(0.1, inplace=True)
# now drop the total variables, we're not interested at all
cols_drop = ['usa total gas sold']
nv_share_usa_total = nv_share_usa_total.drop(columns=cols_drop)

# now merge our 3 datasets of interest:
gas_tax_final_df = pd.merge(nv_share_usa_total, avg_gas_state_tax_df, on='date', how='outer')
gas_tax_final_df = pd.merge(gas_tax_final_df, wa_excise_df, on='date', how='outer')

# now keep only those observations starting with january 01, 2000
gas_tax_final_df = gas_tax_final_df[gas_tax_final_df['date'] >= '2000-01-01']
# now forward fill the ca tax variable
for var in ['nv excise tax']:
    gas_tax_final_df[var] = gas_tax_final_df[var].fillna(method='ffill')

# now let's plot average state tax excl. wa and wa excise tax:
plt.figure(figsize=(12, 6))
plt.plot(gas_tax_final_df['date'], gas_tax_final_df['nv excise tax'],
         label = 'NV Excise Tax', color='blue')
plt.plot(gas_tax_final_df['date'], gas_tax_final_df['average state tax excl. nv'],
         label = 'Average National Tax Excl. NV', color='orange')
plt.legend()
plt.show()

gas_tax_final_df.to_csv(f'{clean_data}/gas_taxes.csv', index=False)