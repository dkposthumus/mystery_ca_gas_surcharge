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
    city_df = rack_detailed_df[rack_detailed_df['rack_city'] == city]
    
    # Keep only the relevant columns
    cols_keep = ['date', 'company', 'branded_indicator', 'location of refiner', 
                 'distributor', var_to_plot]
    city_df = city_df[cols_keep]
    city_df = city_df.fillna({'company': '.', 'branded_indicator': '.', 
                              'location of refiner': '.', 'distributor': '.'})
    city_df_long = pd.melt(city_df, 
                           id_vars=['date', 'company', 'branded_indicator', 
                                    'location of refiner', 'distributor'],
                           value_vars=var_to_plot,
                           var_name='Variable',
                           value_name='Value')
    plt.figure(figsize=(14, 7))
    city_df_long = city_df_long.sort_values(by='date')
    city_df_long['4_month_moving_avg'] = (city_df_long.groupby(['company', 'branded_indicator', 
                                                           'location of refiner', 'distributor', 
                                                           'Variable'])['Value']
                                        .transform(lambda x: x.rolling(window=122, min_periods=1).mean()))
    color_cycle = plt.cm.get_cmap('tab20', len(city_df_long.groupby(['company', 
                                            'branded_indicator', 'location of refiner', 'distributor', 
                                            'Variable'])))
    for i, (key, grp) in enumerate(city_df_long.groupby(['company', 'branded_indicator', 
                                          'location of refiner', 'distributor', 'Variable'])):
        company, branded_indicator, loc_refiner, distributor, var = key
        if company != '.' or branded_indicator != '.' or loc_refiner != '.' or distributor != '.':
            if company == '.' and branded_indicator != '.':
                label = f"{branded_indicator} (total)"
                if branded_indicator == 'branded':
                    plt.plot(grp['date'], grp['4_month_moving_avg'], linewidth=4, label=label, 
                         color='green')
                if branded_indicator == 'unbranded':
                    plt.plot(grp['date'], grp['4_month_moving_avg'], linewidth=4, label=label, 
                         color='blue')
            else:
                label = f"{company}, {branded_indicator}, {loc_refiner}, {distributor}"
                plt.plot(grp['date'], grp['4_month_moving_avg'], label=label, color=color_cycle(i))
    plt.axvline(pd.to_datetime('2015-02-01'), color='red', 
                linestyle='--', linewidth=2, label='Torrance Refinery Fire')
    plt.axhline(y=0, color='black', linestyle='-', linewidth=2.5)
    plt.ylim(-0.6, 0.6)
    plt.title(f'BBG Rack Price Spreads (Real) for {city.title()}, 4-Month Moving Average')
    plt.xlabel('Date')
    plt.ylabel('March 2023 $/Gallon')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{rack_analysis}/{city}_spread.png')
    plt.show()

for city in rack_detailed_df['rack_city'].unique(): 
    city_var_time_series(city, 'bbg gross spread (real)')

def refiner_var_time_series(refiner, var_to_plot):
    # Filter the DataFrame for the specified city
    refiner_df = rack_detailed_df[rack_detailed_df['company'] == refiner]
    refiner_df = refiner_df[refiner_df['branded_indicator'] == 'branded']
    cities_of_interest = ['los angeles', 'san francisco', 'san diego', 'san jose', 'bakersfield']
    refiner_df = refiner_df[refiner_df['rack_city'].isin(cities_of_interest)]
    # Keep only the relevant columns
    cols_keep = ['date', 'rack_city', 'location of refiner', 
                 'distributor', var_to_plot]
    refiner_df = refiner_df[cols_keep]
    refiner_df = refiner_df.fillna({'rack_city': '.', 
                              'location of refiner': '.', 'distributor': '.'})
    refiner_df_long = pd.melt(refiner_df, 
                           id_vars=['date', 'location of refiner', 'distributor', 'rack_city'],
                           value_vars=var_to_plot,
                           var_name='Variable',
                           value_name='Value')
    plt.figure(figsize=(14, 7))
    refiner_df_long = refiner_df_long.sort_values(by='date')
    refiner_df_long['4_month_moving_avg'] = (refiner_df_long.groupby(['rack_city', 
                                                        'location of refiner', 'distributor', 
                                                        'Variable'])['Value']
                                        .transform(lambda x: x.rolling(window=122, min_periods=1).mean()))
    color_cycle = plt.cm.get_cmap('tab20', len(refiner_df_long.groupby(['rack_city', 
                                    'location of refiner', 'distributor', 'Variable'])))
    for i, (key, grp) in enumerate(refiner_df_long.groupby(['rack_city', 
                                          'location of refiner', 'distributor', 'Variable'])):
        city, loc_refiner, distributor, var = key
        if city != '.' or loc_refiner != '.' or distributor != '.':
            label = f'{city}, {loc_refiner}, {distributor}'
            plt.plot(grp['date'], grp['4_month_moving_avg'], label=label, color=color_cycle(i))
    plt.axvline(pd.to_datetime('2015-02-01'), color='red', 
                linestyle='--', linewidth=2, label='Torrance Refinery Fire')
    plt.axhline(y=0, color='black', linestyle='-', linewidth=2.5)
    plt.title(f'BBG Rack Price Spreads (Real) for {refiner.title()}, 4-Month Moving Average')
    plt.xlabel('Date')
    plt.ylabel('March 2023 $/Gallon')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{rack_analysis}/{refiner}_spread.png')
    plt.show()
for refiner in ['chevron', 'conocophillips', 'valero', 'shell']: 
    print(refiner)
    refiner_var_time_series(refiner, 'bbg gross spread (real)')