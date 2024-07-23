import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import matplotlib.dates as mdates

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

# now let's import the master dataset 
master_df = pd.read_csv(f'{data}/master.csv')
# set the index to be equal to the date variable
master_df['date'] = pd.to_datetime(master_df['date'])
master_df.set_index('date', inplace=True)

# now let's find a couple of annual averages that are useful for graphing:
master_df['annual average ca margin (real)'] = master_df.groupby('year')['ca margin (real)'].transform('mean')
master_df['annual average mgs (real)'] = master_df.groupby('year')['unexplained differential (real)'].transform('mean')
master_df['annual average spot price differential (real)'] = master_df.groupby('year')['spot price differential (real)'].transform('mean')
master_df['annual average mgs - spot price differential (real)'] = master_df.groupby('year')['mgs - spot price (real)'].transform('mean')
start_date = pd.to_datetime('2012-01-01')
end_date = pd.to_datetime('2024-06-01')

plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['unexplained differential (real)'], label='Unexplained Differential (Real)')
plt.plot(master_df.index, master_df['annual average mgs (real)'], label='Annual Average MGS (Real)', color='black', linewidth=3)
plt.title('Mystery Gas Surcharge (MGS) (in $2023), 2012-2024')
plt.xlabel('Date')
plt.ylabel('Mystery Gas Surcharge')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(1))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.show()
plt.savefig(f'{output}/unexplained_differential.png')

# now let's make the same plot, but for CA's margin
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['ca margin (real)'], label='CA Margin (Real)')
plt.plot(master_df.index, master_df['annual average ca margin (real)'], label='Annual Average CA Margin (Real)', color='black', linewidth=3)
plt.title('California Margin (in $2023), 2012-2024')
plt.xlabel('Date')
plt.ylabel('Margin')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(1))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.show()
plt.savefig(f'{output}/ca_margin.png')

# now the same plot, but for the spot price differential
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['spot price differential (real)'], label='Spot Price Differential (Real)')
plt.plot(master_df.index, master_df['annual average spot price differential (real)'], label='Annual Average Spot Price Differential (Real)', color='black', linewidth=3)
plt.title('LA Spot Price versus NY/Gulf Average Spot Price (in $2023), 2012-2024')
plt.xlabel('Date')
plt.ylabel('Difference')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(1))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.show()
plt.savefig(f'{output}/spot_differential.png')

# now plot together the mystery gas surcharge and the spot price differential
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['mgs - spot price (real)'], label='MGS - Spot Price Differential (Real)')
plt.plot(master_df.index, master_df['annual average mgs - spot price differential (real)'], label='Average Annual MGS - Spot Price Differential (Real)', linewidth=3, color='black')
plt.title('MGS versus Spot Price Differential (in $2023), 2012-2024')
plt.xlabel('Date')
plt.ylabel('MGS - Spot Price Differential')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(1))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.show()
plt.savefig(f'{output}/mgs_spot_differential.png')