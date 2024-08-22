import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')
rack_analysis = (output / 'ca_city_rack_analyses')

master_df = pd.read_csv(f'{data}/master.csv')
master_df['date'] = pd.to_datetime(master_df['date'])

# define our time-series function:
def plot_city_differentials(df, cities, type_differential, nominalreal, title, ylabel, save_path):
    fig, ax1 = plt.subplots(figsize=(14, 7))
    for city in cities:
        differential_column = f'{city} {type_differential} differential ({nominalreal})'
        if differential_column in df.columns:
            ax1.plot(df['date'], df[differential_column], label=city)
    ax1.set_xlabel('Date')
    ax1.set_ylabel(ylabel)
    ax1.axhline(y=0, color='black', linewidth=2.5) 
    ax1.grid(True)
    #ax2 = ax1.twinx()
    #ax2.set_ylabel('Unexplained Differential (Nominal)', color='tab:red')
    ax1.plot(df['date'], df[f'unexplained differential ({nominalreal})'], color='black',
              label=f'Unexplained Differential ({nominalreal})', linewidth=3)
    #ax2.tick_params(axis='y', labelcolor='tab:red')
    ax1.legend(loc='upper left')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()

cities = ['los angeles', 'fresno', 'bakersfield', 'barstow', 'chico',   
          'colton', 'imperial', 'sacramento', 'san diego', 'san francisco', 
          'san jose', 'stockton']

# now create a spot-rack differential for each city:
for city in cities:
    master_df[f'{city} rack-spot differential (nominal)'] = (
        master_df[f'{city} rack price'] - master_df['la spot price (nominal)']
    )
    master_df[f'{city} retail-rack differential (nominal)'] = (
        master_df['california gas (retail) (nominal)'] - master_df[f'{city} rack price']
    )
    for var in ['rack-spot', 'retail-rack']:
        master_df[f'{city} {var} differential (real)'] = (master_df[f'{city} {var} differential (nominal)']
                                                          /master_df['price deflator'])
plot_city_differentials(master_df, cities, 'rack-spot', 'real',
                        'Rack-Spot Price Differential by City and Mystery Gas Surcharge (MGS) (Real)', 
                        'Rack-Spot Price Differential (Current $)', 
                        f'{rack_analysis}/rack_spot_differentials.png')
plot_city_differentials(master_df, cities, 'retail-rack', 'real',
                        'Retail-Rack Price Differential by City and Mystery Gas Surcharge (MGS) (Real)',
                        'Retail-Rack Price Differential (Current $)',
                        f'{rack_analysis}/retail_rack_differentials.png')