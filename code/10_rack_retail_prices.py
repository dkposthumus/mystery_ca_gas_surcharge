import requests
import pandas as pd
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

rack_prices_df = pd.read_excel(f'{raw_data}/bloomberg_rack_prices.xlsx', 
                               sheet_name='ca_rack_import')
rack_prices_df.rename(
    columns={
        'Date': 'date', 
        'RACKM0G PO6 R Index': 'los angeles rack price',
        'RACKK0G PO6 R Index': 'fresno rack price',   
        'RACKE0G PO6 R Index': 'bakersfield rack price',
        'RACKF0G PO6 R Index': 'barstow rack price',
        'RACKH0G PO6 R Index': 'chico rack price',
        'RACKI0G PO6 R Index': 'colton rack price',
        'RACKL0G PO6 R Index': 'imperial rack price',
        'RACKN0G PO6 R Index': 'sacramento rack price',
        'RACKO0G PO6 R Index': 'san diego rack price',
        'RACKP0G PO6 R Index': 'san francisco rack price',
        'RACKQ0G PO6 R Index': 'san jose rack price',
        'RACKR0G PO6 R Index': 'stockton rack price',
    }, 
    inplace=True
)
rack_prices_df['date'] = pd.to_datetime(rack_prices_df['date'])

rack_prices_df = (rack_prices_df.groupby(pd.Grouper(key='date', freq='MS'))
                          .agg('mean').reset_index())

rack_prices_df.to_csv(f'{data}/rack_prices.csv', index=False)