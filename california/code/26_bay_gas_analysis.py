import pandas as pd
from pathlib import Path
from typing import List, Tuple
import numpy as np
import osmnx as ox
import networkx as nx
from collections import defaultdict
from math import radians, sin, cos, sqrt, atan2
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

ca_retail = pd.read_excel(raw_data / 'ca_retail.xls', sheet_name='Data 1', skiprows=2)
sf_retail = pd.read_excel(raw_data / 'sf_retail.xls', sheet_name = 'Data 1', skiprows=2)

for df, name, label in zip([ca_retail, sf_retail], ['California', 'San Francisco'], ['Statewide', 'SF']):
    df.rename(columns={
        f'Weekly {name} All Grades All Formulations Retail Gasoline Prices  (Dollars per Gallon)': 'retail (nominal)',
        }, inplace=True)
    df['date'] = pd.to_datetime(df['Date'])
    # restrict to post-2020
    plt.plot(df['date'], df['retail (nominal)'], label=f'{label}')
plt.axvline(pd.to_datetime('2015-02-01'), color='red', linestyle='--', label='Torrance Refinery Fire')
plt.legend()
plt.title('Retail Gas Prices')
plt.show()

# first, restrict to post-2020 data
for df, name, label in zip([ca_retail, sf_retail], ['California', 'San Francisco'], ['Statewide', 'SF']):
    df.rename(columns={
        f'Weekly {name} All Grades All Formulations Retail Gasoline Prices  (Dollars per Gallon)': 'retail (nominal)',
        }, inplace=True)
    df['date'] = pd.to_datetime(df['Date'])
    # restrict to post-2020
    begin_date = pd.to_datetime('2020-01-01')
    post_2020 = df[df['date'] > begin_date]
    plt.plot(post_2020['date'], post_2020['retail (nominal)'], label=f'{label}')
plt.legend()
plt.title('Retail Gas Prices')
plt.show()

for df, name, label in zip([ca_retail, sf_retail], ['California', 'San Francisco'], ['Statewide', 'SF']):
    df.rename(columns={
        f'Weekly {name} All Grades All Formulations Retail Gasoline Prices  (Dollars per Gallon)': 'retail (nominal)',
        }, inplace=True)
    df['date'] = pd.to_datetime(df['Date'])
    # restrict to post-2020
    begin_date = pd.to_datetime('2024-01-01')
    post_2024 = df[df['date'] > begin_date]
    plt.plot(post_2024['date'], post_2024['retail (nominal)'], label=f'{label}')
plt.legend()
plt.title('Retail Gas Prices')
plt.show()

master = pd.merge(ca_retail, sf_retail, on='date', suffixes=('_ca', '_sf'))
master['diff'] = master['retail (nominal)_sf'] - master['retail (nominal)_ca']
# first plot raw difference, lightly
plt.plot(master['date'], master['diff'], label='Un-Adjusted', alpha=0.5)
# then take moving average (6-month let's say)
plt.plot(master['date'], master['diff'].rolling(26).mean(), label='6-Month MA')
plt.title('SF Gas Price - CA Gas Price')
plt.axvline(pd.to_datetime('2015-02-01'), color='red', linestyle='--', label='Torrance Refinery Fire')
# now let's add horizontal line at y=0
plt.axhline(0, color='black', linestyle='-')
plt.legend()
plt.show()

master.to_csv(f'{data}/ca_sf_retail.csv', index=False)