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

# let's find the average spot price between nyc and gulf coast 
master_df['natl spot price excl. ca (nominal)'] = (master_df['gulf spot price (nominal)'] 
                                                   + master_df['ny spot price (nominal)'])/2
for var in ['ca total fees and taxes', 'average state tax excl. ca',]:
    master_df[f'{var} (nominal)'] = master_df[var]
# let's convert some variable from nominal to real 
for var in ['california gas (retail)', 'national retail excl. ca',
            'la spot price', 'natl spot price excl. ca',
            'ca total fees and taxes', 'average state tax excl. ca',
            ]:
    master_df[f'{var} (real)'] = master_df[f'{var} (nominal)']/master_df['price deflator']

# now let's find a couple of annual averages that are useful for graphing:
for var in ['ca margin (real)', 'unexplained differential (real)',
            'spot price differential (real)', 'mgs - spot price differential (real)',
            'california gas (retail) (real)', 'national retail excl. ca (real)',
            'la spot price (real)', 'natl spot price excl. ca (real)',
            'ca total fees and taxes (real)', 'average state tax excl. ca (real)',
            ]:
    master_df[f'annual average {var}'] = master_df.groupby('year')[var].transform('mean')
start_date = pd.to_datetime('2000-01-01')
end_date = pd.to_datetime('2024-06-01')

plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['unexplained differential (real)'], 
         label='Unexplained Differential (Real)')
plt.plot(master_df.index, master_df['annual average unexplained differential (real)'], 
         label='Annual Average MGS (Real)', 
         color='black', linewidth=3)
plt.title('Mystery Gas Surcharge (MGS) (in $2023), 2000-2024')
plt.xlabel('Date')
plt.ylabel('Mystery Gas Surcharge')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/unexplained_differential.png')
plt.show()

# now let's make the same plot, but for CA's margin
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['ca margin (real)'], label='CA Margin (Real)')
plt.plot(master_df.index, master_df['annual average ca margin (real)'], label='Annual Average CA Margin (Real)', color='black', linewidth=3)
plt.title('California Margin (in $2023), 2000-2024')
plt.xlabel('Date')
plt.ylabel('Margin')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/ca_margin.png')
plt.show()

# now the same plot, but for the spot price differential
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['spot price differential (real)'], 
         label='Spot Price Differential (Real)')
plt.plot(master_df.index, master_df['annual average spot price differential (real)'], 
         label='Annual Average Spot Price Differential (Real)', 
         color='black', linewidth=3)
plt.plot(master_df.index, master_df['unexplained differential (real)'],
         label='Mystery Gas Surcharge (Real)')
plt.plot(master_df.index, master_df['annual average unexplained differential (real)'],
         label='Average Annual MGS (Real)',
         color='red', linewidth=3)
plt.title('LA Spot Price versus NY/Gulf Average Spot Price  and MGS (in $2023)')
plt.xlabel('Date')
plt.ylabel('Difference')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 
plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')
plt.legend()
plt.savefig(f'{output}/spot_differential.png')
plt.savefig(f'{output}/ca_city_rack_analyses/spot_differential.png')
plt.show()

# now plot together the mystery gas surcharge and the spot price differential
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['mgs - spot price differential (real)'], 
         label='MGS - Spot Price Differential (Real)')
plt.plot(master_df.index, master_df['annual average mgs - spot price differential (real)'], 
         label='Average Annual MGS - Spot Price Differential (Real)', linewidth=3, color='black')
plt.title('MGS with Spot Price Difference Extracted Out (in $2023), 2003-2024')
plt.xlabel('Date')
plt.ylabel('MGS - Spot Price Difference')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/mgs_spot_differential.png')
plt.show()

# let's plot CA and the rest of the country's retail prices, including the annual averages 
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['california gas (retail) (real)'], 
         label='CA Retail Price',
         color='blue')
plt.plot(master_df.index, master_df['annual average california gas (retail) (real)'], 
         label='Average Annual CA Retail Price', 
         linewidth=3, color='blue')
plt.plot(master_df.index, master_df['national retail excl. ca (real)'], 
         label='Rest of Country Retail Price',
         color='orange')
plt.plot(master_df.index, master_df['annual average national retail excl. ca (real)'], 
         label='Average Annual Rest of Country Retail Price', 
         linewidth=3, color='orange')
plt.title('CA vs. Rest of Country Gas Retail Prices (in $2023), 2000-2024')
plt.xlabel('Date')
plt.ylabel('Retail Gasoline Price')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/ca_natl_retail.png')
plt.show()

# let's plot CA and the rest of the country's retail prices, including the annual averages 
plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['la spot price (real)'], 
         label='LA Spot Price',
         color='blue')
plt.plot(master_df.index, master_df['annual average la spot price (real)'], 
         label='Average Annual LA Spot Price', 
         linewidth=3, color='blue')
plt.plot(master_df.index, master_df['natl spot price excl. ca (real)'], 
         label='NY/Gulf Average Spot Price',
         color='orange')
plt.plot(master_df.index, master_df['annual average natl spot price excl. ca (real)'], 
         label='Average Annual NY/Gulf Spot Price', 
         linewidth=3, color='orange')
plt.title('CA vs. NY/Gulf Spot Price (in $2023), 2003-2024')
plt.xlabel('Date')
plt.ylabel('Spot Price')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/ca_natl_spot.png')
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['ca total fees and taxes (real)'], 
         label='CA Total Fees and Taxes',
         color='blue')
plt.plot(master_df.index, master_df['average state tax excl. ca (real)'], 
         label='Average State Excise Tax Excl. CA',
         color='orange')
plt.title('CA vs. Rest of Country Taxes and Fees (in $2023), 2000-2024')
plt.xlabel('Date')
plt.ylabel('Taxes and Fees')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.set_xlim([start_date, end_date]) 

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.savefig(f'{output}/ca_natl_fees_taxes.png')
plt.show()