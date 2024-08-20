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

rack_detailed_df = pd.read_csv(f'{data}/detailed_rack_prices.csv')
rack_detailed_df['date'] = pd.to_datetime(rack_detailed_df['date'], format='mixed')

def plot_time_series(vars_of_interest, city, save_path=None):
    plt.figure(figsize=(14, 7))
    for var in vars_of_interest:
        plt.plot(temp_df['date'], temp_df[f'{var} spread 6 month m.a. (real)'], label=var)
    plt.axvline(pd.to_datetime('2015-02-01'), color='black', linestyle='--', 
                linewidth=2, label='Torrance Refinery Fire')
    plt.axhline(y=0, color='black', linestyle='-', linewidth=2.5)
    plt.title(f'{city} Rack Price Spreads, 4-Month Moving Average')
    plt.xlabel('Year')
    plt.ylabel('Value')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()

cities = ['los angeles', 'fresno', 'barstow', 'chico', 'colton', 'imperial', 
                     'sacramento', 'san diego', 'san francisco', 'san jose', 'stockton',
                     'bakersfield']
for city in cities:
    temp_df = rack_detailed_df[[col for col in rack_detailed_df.columns 
                                if col == 'date' or col == 'price deflator' or city in col]]
    phrase = f'{city} rack price'
    vars_city = [var for var in temp_df.columns if phrase not in var and var!= 'date' 
                 and var != 'price deflator']
    vars_interest = [
        var.replace(' Index spread (nominal)', '').replace(' Index', '') for var in vars_city 
    ]
    for var in vars_interest:
        temp_df[f'{var} spread (real)'] = (temp_df[f'{var} Index spread (nominal)']
                                         /temp_df['price deflator'])
        temp_df[f'{var} spread 6 month m.a. (real)'] = (temp_df[f'{var} spread (real)']
                                              .rolling(window=122, min_periods=1).mean())
    plot_time_series(vars_interest, city, 
                 f'{output}/ca_city_rack_analyses/{city}_rack_prices.png')
    vars_interest = [f'{city} unbranded rack', f'{city} branded rack']
    plot_time_series(vars_interest, city, 
                 f'{output}/ca_city_rack_analyses/{city}_rack_prices_branded_unbranded.png')