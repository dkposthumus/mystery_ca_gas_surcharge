import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

master_df = pd.read_csv(f'{data}/master.csv')
master_df['date'] = pd.to_datetime(master_df['date'])

cec_df = pd.read_excel(f'{raw_data}/cec_price_margins_data.xlsx', sheet_name='Data')
cec_df = cec_df.pivot(index=['Date', 'BrandedUnbranded'], columns='PriceType', values='Price')
cec_df.reset_index(inplace=True)
cec_df = cec_df.pivot(index='Date', columns='BrandedUnbranded')
cec_df.columns = [' '.join(col).strip() for col in cec_df.columns.values]
cec_df.reset_index(inplace=True)
cec_df.rename(columns={'Date': 'date'}, inplace=True)
cec_df['date'] = pd.to_datetime(cec_df['date'])

merged_df = pd.merge(cec_df, master_df, on='date', how='outer')
merged_df['date'] = pd.to_datetime(merged_df['date'])
merged_df = merged_df.fillna(method='ffill')

# let's create a basic series of plots comparing mgs to interesting variables 
start_date = pd.to_datetime('2000-01-01')
end_date = pd.to_datetime('2024-06-01')

plt.figure(figsize=(10, 6))
plt.plot(merged_df['date'], merged_df['Distribution Costs, Marketing Costs, and Profits Branded'], 
         label='Distribution Margin, Branded')
plt.plot(merged_df['date'], merged_df['Distribution Costs, Marketing Costs, and Profits Unbranded'], 
         label='Distribution Margin, Unbranded')
plt.plot(merged_df['date'], merged_df['unexplained differential (nominal)'], 
         label='MGS', linewidth=3)
plt.title('Mystery Gas Surcharge (MGS) vs. Distribution Margin (Nominal), 2000-2024')
plt.xlabel('Date')
plt.ylabel('Nominal $')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/cec_costs_1.png')
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(merged_df['date'], merged_df['Refinery Costs and Profits Branded'], 
         label='Refinery Margin, Branded')
plt.plot(merged_df['date'], merged_df['Refinery Costs and Profits Unbranded'], 
         label='Refinery Margin, Unbranded')
plt.plot(merged_df['date'], merged_df['unexplained differential (nominal)'], 
         label='MGS', linewidth=3)
plt.title('Mystery Gas Surcharge (MGS) vs. Refinery Gross Margin (Nominal), 2000-2024')
plt.xlabel('Date')
plt.ylabel('Nominal $')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/cec_costs_2.png')
plt.show()

merged_df['unbranded branded price difference'] = merged_df['Average Retail prices Branded'] - merged_df['Average Retail prices Unbranded']

plt.figure(figsize=(10, 6))
ax = plt.gca()
ax.plot(merged_df['date'], merged_df['unbranded branded price difference'],
        label='Branded - Unbranded Price Difference', color='blue')
ax.set_xlabel('Date')
ax.set_ylabel('Nominal $', color='blue')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date])
ax.grid(True)
ax.tick_params(axis='y', labelcolor='blue')
ax2 = ax.twinx()
ax2.plot(merged_df['date'], merged_df['unexplained differential (nominal)'], 
         label='MGS', linewidth=3, color='green')
ax2.set_ylabel('Nominal $', color='green')
ax2.tick_params(axis='y', labelcolor='green')
ax.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.title('Unbranded vs. Branded CA Retail Gasoline Prices (Nominal), 2000-2024')
lines_1, labels_1 = ax.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
plt.savefig(f'{output}/cec_price_comp.png')
plt.show()