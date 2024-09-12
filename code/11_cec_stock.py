import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
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
def plot_time_series(df, value_col, title, ylabel):
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

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45) 
    plt.tight_layout()
    plt.legend()
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
                     f'{var} Over Time -- California Total, CARB Reformulated Gasoline', lab)

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