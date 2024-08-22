import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')
rack_analysis = (output / 'ca_city_rack_analyses')

rack_detailed_df = pd.read_csv(f'{data}/detailed_rack_prices.csv')
rack_detailed_df['date'] = pd.to_datetime(rack_detailed_df['date'], format='mixed')

def city_var_time_series(city, var_to_plot):
    # Filter the DataFrame for the specified city
    city_df = rack_detailed_df[rack_detailed_df['rack fuel location'] == city]
    
    # Keep only the relevant columns
    cols_keep = ['date', 'refiner', 'branded.unbranded', 'location of refiner', 
                 'distributor', var_to_plot]
    city_df = city_df[cols_keep]
    city_df = city_df.fillna({'refiner': '.', 'branded.unbranded': '.', 
                              'location of refiner': '.', 'distributor': '.'})
    city_df_long = pd.melt(city_df, 
                           id_vars=['date', 'refiner', 'branded.unbranded', 
                                    'location of refiner', 'distributor'],
                           value_vars=var_to_plot,
                           var_name='Variable',
                           value_name='Value')
    plt.figure(figsize=(14, 7))
    city_df_long = city_df_long.sort_values(by='date')
    city_df_long['4_month_moving_avg'] = (city_df_long.groupby(['refiner', 'branded.unbranded', 
                                                           'location of refiner', 'distributor', 
                                                           'Variable'])['Value']
                                        .transform(lambda x: x.rolling(window=122, min_periods=1).mean()))
    for key, grp in city_df_long.groupby(['refiner', 'branded.unbranded', 
                                          'location of refiner', 'distributor', 'Variable']):
        refiner, branded_unbranded, loc_refiner, distributor, var = key
        if refiner != '.' or branded_unbranded != '.' or loc_refiner != '.' or distributor != '.':
            if refiner == '.' and branded_unbranded != '.':
                label = f"{branded_unbranded} (total)"
                plt.plot(grp['date'], grp['4_month_moving_avg'], linewidth=4, label=label)
            else:
                label = f"{refiner}, {branded_unbranded}, {loc_refiner}, {distributor}"
                plt.plot(grp['date'], grp['4_month_moving_avg'], label=label)
    plt.axvline(pd.to_datetime('2015-02-01'), color='red', 
                linestyle='--', linewidth=2, label='Torrance Refinery Fire')
    plt.title(f'Rack Price Spreads (Real) for {city.title()}')
    plt.xlabel('Date')
    plt.ylabel('March 2023 $/Gallon')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{rack_analysis}/{city}_spread.png')
    plt.show()

for city in rack_detailed_df['rack fuel location'].unique(): 
    city_var_time_series(city, 'spread (real)')
