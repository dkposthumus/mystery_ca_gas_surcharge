import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import matplotlib.dates as mdates

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge' / 'washington_state')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
ca_data = (home_dir / 'mystery_ca_gas_surcharge' / 'data')
code = Path.cwd() 
output = (work_dir / 'output')

# now let's import the master dataset 
master_df = pd.read_csv(f'{clean_data}/master.csv')
# set the index to be equal to the date variable
master_df['date'] = pd.to_datetime(master_df['date'])
master_df.set_index('date', inplace=True)

'''# let's find the average spot price between nyc and gulf coast 
master_df['natl spot price excl. ca (nominal)'] = (master_df['gulf spot price (nominal)'] 
                                                   + master_df['ny spot price (nominal)'])/2
for var in ['ca total fees and taxes', 'average state tax excl. ca',]:
    master_df[f'{var} (nominal)'] = master_df[var]
# let's convert some variable from nominal to real 
for var in ['california gas (retail)', 'national retail excl. ca',
            'la spot price', 'natl spot price excl. ca',
            'ca total fees and taxes', 'average state tax excl. ca',
            ]:
    master_df[f'{var} (real)'] = master_df[f'{var} (nominal)']/master_df['price deflator']'''

# now let's find a couple of annual averages that are useful for graphing:
vars = ['ca margin (real)', 'unexplained differential (real)',
            'spot price differential (real)', 'mgs - spot price differential (real)',
            'california gas (retail) (real)', 'national retail excl. ca (real)',
            'la spot price (real)', 'natl spot price excl. ca (real)',
            'ca total fees and taxes (real)', 'average state tax excl. ca (real)',
            ]
for var in ['unexplained differential (real)']:
    master_df[f'annual average {var}'] = master_df.groupby('year')[var].transform('mean')
start_date = pd.to_datetime('2003-01-01')
end_date = pd.to_datetime('2024-06-01')

plt.figure(figsize=(10, 6))
plt.plot(master_df.index, master_df['unexplained differential (real)'], 
         label='Unexplained Differential (Real)')
plt.plot(master_df.index, master_df['annual average unexplained differential (real)'], 
         label='Annual Average MGS (Real)', 
         color='black', linewidth=3)
plt.title('Washington Mystery Gas Surcharge (MGS) (in $2023), 2000-2024')
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

# now let's bring in the california mystery gasoline surcharge
ca_mgs = pd.read_csv(f'{ca_data}/master.csv')
ca_mgs = ca_mgs[['date', 'unexplained differential (real)']]
ca_mgs['date'] = pd.to_datetime(ca_mgs['date'])
# now bring in wa_mgs 
wa_mgs = pd.read_csv(f'{clean_data}/wa_mgs_real.csv')
wa_mgs['date'] = pd.to_datetime(wa_mgs['date'])

graphing_comp = pd.merge(wa_mgs, ca_mgs, on='date', how='inner')
graphing_comp['year'] = graphing_comp['date'].dt.year
# calculate annual average of unexplained differential
for var in ['unexplained differential (real)', 'wa_mgs_real']:
    graphing_comp[f'annual average {var}'] = graphing_comp.groupby('year')[var].transform('mean')

# now plot to compare over time
start_date = pd.to_datetime('2003-01-01')
end_date = pd.to_datetime('2024-06-01')
plt.figure(figsize=(10, 6))
plt.plot(graphing_comp['date'], graphing_comp['unexplained differential (real)'], 
         label='CA MGS (Real)', alpha=0.7, color='blue')
plt.plot(graphing_comp['date'], graphing_comp['annual average unexplained differential (real)'], 
         label='CA Annual Average MGS (Real)', 
         color='blue', linewidth=1.5)

plt.plot(graphing_comp['date'], graphing_comp['wa_mgs_real'], 
         label='WA MGS (Real)', alpha=0.7, color='orange')
plt.plot(graphing_comp['date'], graphing_comp['annual average wa_mgs_real'], 
         label='WA Annual Average MGS (Real)', 
         color='orange', linewidth=1.5)

plt.title('Washington vs. California Mystery Gas Surcharge (MGS) (in $2023), 2000-2024')
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