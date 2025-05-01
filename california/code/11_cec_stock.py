import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
import requests
import json
# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

cec_stock_raw_df = pd.read_excel(f'{raw_data}/cec_inventory_production.xlsx', sheet_name='Data')

cec_stock_df = cec_stock_raw_df.copy()

''' 
3 requests/questions for this data: 
- What were inventories Aug 1, 2023, as a percentile of the 2015-2019 distribution? 
- What were they as a percent of the 2015-2019 average?
- What were inventories in terms of days supplied?
'''

#cec_stock_df['Date'] = pd.to_datetime(cec_stock_df['Date'])
# now pull helpful time identifiers
cec_stock_df['day'] = cec_stock_df['Date'].dt.day
cec_stock_df['month'] = cec_stock_df['Date'].dt.month
cec_stock_df['year'] = cec_stock_df['Date'].dt.year

# first filter data to only include CARB 
cec_stock_df = cec_stock_df[cec_stock_df['Product Type'] == 'CARB Reformulated Gasoline']

# now combine Northern California and Southern California into one
cec_stock_total_ca_df = cec_stock_df.groupby(['Date', 'Product Type', 'Product Category', 
                                     'Throughput Type', 'day', 'month', 'year']).sum().reset_index()
# since we're only dealing with CARB, the only unique value for 'Throughout Type' is 'Production'.
# thus, we can drop it, along with the other constant variables.
cec_stock_total_ca_df.drop(columns=['Region', 'Product Category', 'Throughput Type'], inplace=True)

# before finding numbers let's plot the time-series to get a sense of what we're working with
def plot_time_series(df, value_col, title, ylabel, _5yr_plot, save):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df[value_col], color='blue', linestyle='-', 
             label = f'{value_col}, Raw', linewidth=0.25)

    df[f'{value_col}_6month_ma'] = df[value_col].rolling(window=24).mean()
    plt.plot(df['Date'], df[f'{value_col}_6month_ma'], color='blue', linestyle='-', 
             label=f'{value_col}, 6-Month Moving Average', linewidth=2)

    plt.axvline(pd.to_datetime('2023-08-04'), color='red', linestyle='--', 
                linewidth=2, label='August 04, 2023')

    plt.axvline(pd.to_datetime('2015-02-20'), color='red', linestyle='--', 
               linewidth=2, label='Torrance Refinery Fire (February 20, 2015)')

    if _5yr_plot == True:
        plt.fill_between(df['Date'], df['5yr_min'], df['5yr_max'], color='gray', 
                        alpha=0.5, label='5-yr Range')

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45) 
    plt.tight_layout()
    plt.legend()
    if save == True:
        plt.savefig(f'{output}/cec_{value_col.lower()}.png')
    plt.show()

# make a days supplied variable, which is just stocks divided by throughput
    # multiply by 7 so that this is in terms of days, not weeks
cec_stock_total_ca_df['Days Supplied'] = (cec_stock_total_ca_df['Stocks'] 
                                        / cec_stock_total_ca_df['Throughput']) * 7

for var, lab in zip(['Stocks', 'Throughput', 'Days Supplied'], ['Stocks, 000s of Barrels', 
                                                                'Throughput, 000s of Barrels', 
                                                                'Days Supplied']):
    plot_time_series(cec_stock_total_ca_df, var, 
                     f'{var} Over Time -- California Total, CARB Reformulated Gasoline', lab,
                     _5yr_plot=False, save=True)

# first we need to pinpoint whether we have data for Aug 1, 2023
filtered_df = (cec_stock_total_ca_df[(cec_stock_total_ca_df['month'] == 8) 
                                     & (cec_stock_total_ca_df['year'] == 2023)])
#print(filtered_df['Date'].unique())
filtered_df = (cec_stock_total_ca_df[(cec_stock_total_ca_df['month'] == 2) 
                                     & (cec_stock_total_ca_df['year'] == 2015)])
#print(filtered_df['Date'].unique())

# so the closest date to '2023-08-01' is '2023-08-04'. 
# this is the date i'll use to calculate percentiles.
aug_4_2023_stocks = cec_stock_total_ca_df.loc[cec_stock_total_ca_df['Date'] == '2023-08-04', 
                                              'Stocks'].values[0]
aug_4_2023_throughput = cec_stock_total_ca_df.loc[cec_stock_total_ca_df['Date'] == '2023-08-04', 
                                                  'Throughput'].values[0]

df_2015_2019 = cec_stock_total_ca_df[(cec_stock_total_ca_df['Date'] >= '2015-01-01') 
                                     & (cec_stock_total_ca_df['Date'] <= '2019-12-31')]
# Calculate percentile for August 1, 2023
percentile = percentileofscore(df_2015_2019['Stocks'], aug_4_2023_stocks)
# Calculate the average of 2015-2019 stocks
average_stocks_2015_2019 = df_2015_2019['Stocks'].mean()
# Calculate the percentage of the average
percent_of_average = (aug_4_2023_stocks / average_stocks_2015_2019) * 100
# Calculate days of supply for August 1, 2023
aug_4_2023_days_supplied = (aug_4_2023_stocks / aug_4_2023_throughput) * 7
percentile, percent_of_average, aug_4_2023_days_supplied

# Calculate 5-year rolling minimum and maximum for 'Stock'
cec_stock_total_ca_df['week'] = cec_stock_total_ca_df['Date'].dt.isocalendar().week

# Create empty columns for 5yr_min and 5yr_max
cec_stock_total_ca_df['5yr_min'] = None
cec_stock_total_ca_df['5yr_max'] = None
for idx, row in cec_stock_total_ca_df.iterrows():
    current_year = row['year']
    current_week = row['week']
    
    # Filter the data for the same week in the past 5 years
    last_5_years = (cec_stock_total_ca_df[(cec_stock_total_ca_df['week'] == current_week) 
                                        & (cec_stock_total_ca_df['year'] < current_year) 
                                        & (cec_stock_total_ca_df['year'] >= current_year - 5)])
    
    # Calculate the 5-year min and max for that specific week
    if not last_5_years.empty:
        cec_stock_total_ca_df.at[idx, '5yr_min'] = last_5_years['Stocks'].min()
        cec_stock_total_ca_df.at[idx, '5yr_max'] = last_5_years['Stocks'].max()

# Convert the min/max columns to numeric
cec_stock_total_ca_df['5yr_min'] = pd.to_numeric(cec_stock_total_ca_df['5yr_min'], errors='coerce')
cec_stock_total_ca_df['5yr_max'] = pd.to_numeric(cec_stock_total_ca_df['5yr_max'], errors='coerce')

plot_time_series(cec_stock_total_ca_df, 'Stocks', 
                 'Stock Over Time -- California Total, CARB Reformulated Gasoline', 
                 'Stocks, 000s of Barrels', _5yr_plot=True, save=False)

# filter dataset to include only 2021-2024
shortened_cec_df = (cec_stock_total_ca_df.loc[(cec_stock_total_ca_df['Date'] >= '2021-01-01') 
                        & (cec_stock_total_ca_df['Date'] <= '2024-08-31')])
def plot_shortened_time_series(df, value_col, title, ylabel, _5yr_plot, save):
    plt.figure(figsize=(10, 6))
    plt.plot(df['Date'], df[value_col], color='blue', linestyle='-', 
             label = f'{value_col}, Raw', linewidth=1.5)

    plt.axvline(pd.to_datetime('2023-08-04'), color='red', linestyle='--', 
                linewidth=2, label='August 04, 2023')
    plt.axvline(pd.to_datetime('2022-08-05'), color='red', linestyle='--', 
                linewidth=2, label='August 05, 2022')
    plt.axvline(pd.to_datetime('2021-08-06'), color='red', linestyle='--', 
                linewidth=2, label='August 06, 2023')
    if _5yr_plot == True:
        plt.fill_between(df['Date'], df['5yr_min'], df['5yr_max'], color='gray', 
                        alpha=0.5, label='5-yr Range')

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45) 
    plt.tight_layout()
    plt.legend()
    if save == True:
        plt.savefig(f'{output}/cec_{value_col.lower()}_5y_range.png')
    plt.show()

plot_shortened_time_series(shortened_cec_df, 'Stocks', 
                 'Stock Over Time -- California Total, CARB Reformulated Gasoline', 
                 'Stocks, 000s of Barrels', _5yr_plot=True, save=True)

api_url = 'https://api.eia.gov/v2/petroleum/stoc/st/data'
params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}
header = {
    "frequency": "monthly",
    "data": ["value"],
    "facets": {"duoarea": ["R50", "SCA"],
    "product": ["EPOBG"]},
    "start": "1982-08-20",
    "end": "2024-09-06",
    "sort": [{"column": "period", "direction": "desc"}],
    "offset": 0,
    "length": 5000
}
padd5_stocks = requests.get(
    api_url, params=params, headers={'X-Params': json.dumps(header)}
)
if padd5_stocks.status_code == 200:
    padd5_stocks_data = padd5_stocks.json()
    padd5_stocks_series = padd5_stocks_data['response']['data']
    padd5_stocks_values = []
    for data_point in padd5_stocks_series:
        date = data_point['period']
        stock = data_point['value']
        state = data_point['duoarea']
        padd5_stocks_values.append(
            {
                'Date': date,
                'padd5 monthly stock': stock,
                'state': state
            }
        )
    # Create Pandas DataFrame
    padd5_stocks_df = pd.DataFrame(padd5_stocks_values)
    # Display DataFrame
    print(padd5_stocks_df)
else:
    print(f'Failed to retrieve data. Status code: {padd5_stocks.status_code}')

api_url = 'https://api.eia.gov/v2/petroleum/cons/psup/data'
params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}
header = {"frequency": "monthly",
    "data": ["value"],
    "facets": {"duoarea": ["R50"],
        "product": ["EPM0C"],
        "series": ["MG4UP_R50_1"]},
    "start": "1936-01",
    "end": "2024-06",
    "sort": [{"column": "period", "direction": "desc"}],
    "offset": 0,
    "length": 5000}
padd5_product_supplied = requests.get(
    api_url, params=params, headers={'X-Params': json.dumps(header)}
)
if padd5_stocks.status_code == 200:
    padd5_product_supplied_data = padd5_product_supplied.json()
    padd5_product_supplied_series = padd5_product_supplied_data['response']['data']
    padd5_product_supplied_values = []
    for data_point in padd5_product_supplied_series:
        date = data_point['period']
        stock = data_point['value']
        padd5_product_supplied_values.append(
            {
                'Date': date,
                'padd5 monthly product supplied': stock,
            }
        )
    # Create Pandas DataFrame
    padd5_product_supplied_df = pd.DataFrame(padd5_product_supplied_values)
    # Display DataFrame
    print(padd5_product_supplied_df)
else:
    print(f'Failed to retrieve data. Status code: {padd5_product_supplied.status_code}')
# now merge everything together 
for df in [padd5_stocks_df, padd5_product_supplied_df]:
    for var in df.columns:
        df[var] = pd.to_numeric(df[var], errors='ignore')
    df['Date'] = pd.to_datetime(df['Date'])

padd5_product_supplied_df['padd5 monthly product supplied'] = (
    padd5_product_supplied_df['padd5 monthly product supplied'])
'''
padd5_stocks_df['year'] = padd5_stocks_df['Date'].dt.year
padd5_stocks_df['month'] = padd5_stocks_df['Date'].dt.month
padd5_stocks_df['day'] = 1
padd5_stocks_df = padd5_stocks_df.groupby(['year', 'month']).mean().reset_index()
padd5_stocks_df['Date'] = pd.to_datetime(padd5_stocks_df[['year', 'month', 'day']])
'''
master_df = pd.merge(padd5_stocks_df, padd5_product_supplied_df, on=['Date'], 
                     how='outer')

master_df['days of supply'] = (master_df['padd5 monthly stock'] 
                               / master_df['padd5 monthly product supplied'])
plot_time_series(master_df, 'days of supply',
                    'Days of Supply Over Time -- PADD 5, Conventional Motor Gasoline', 
                    'Days of Supply', _5yr_plot=False, save=True)