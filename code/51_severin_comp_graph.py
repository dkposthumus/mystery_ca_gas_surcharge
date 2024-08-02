import requests
import pandas as pd
import json
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 

# define my master and severin data and then merge to effectively compare the two
severin = f'{data}/severin.csv'
severin_df = pd.read_csv(severin)

master = f'{data}/master.csv'
master_df = pd.read_csv(master)

comp_df = pd.merge(severin_df, master_df, on='date', how='outer')
comp_df['date'] = pd.to_datetime(comp_df['date'])
comp_df.set_index('date', inplace=True)

# plots start at 01/01/2014: 
start_date = pd.to_datetime('2000-01-01')

# for the sake of comparison:
    # since severin includes the federal tax in his calculation of CA's total fees/taxes, add it in here
    # since severin excludes it, subtract the carb cost premium
comp_df['ca total fees and taxes'] = comp_df['ca total fees and taxes'] + 18.4 - comp_df['carb cost premium']

# also add excise and state/local sales tax together
comp_df['ca state.local tax cost'] = comp_df['ca state.local tax cost'] + comp_df['ca state gas tax']

# now i want to create time-series comparing a series of key variables: 
key_var = [
    'ca total fees and taxes', 'cax cost', 'lcfs cost', 'national retail excl. ca (nominal)',
    'california gas (retail) (nominal)', 'average state tax excl. ca', 
    'ca state.local tax cost', 'unexplained differential (real)', 
    'ca total gas sold', 'monthly cost of surcharge (millions)',
    'average daily cost of mgs (millions)'
]
for var in key_var: 
    plt.figure(figsize=(10, 6))
    plt.plot(comp_df.index, comp_df[var], label=var)
    plt.plot(comp_df.index, comp_df[var + ' (severin)'], label=var + ' (severin)')
    plt.title(f"Time Series Comparison: {var} vs {var + '(severin)'}")
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.set_xlim([start_date, comp_df.index.max()]) 
    plt.show()