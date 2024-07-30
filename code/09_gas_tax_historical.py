import requests
import pandas as pd
import json
from pathlib import Path

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 

gas_tax_historical_df = pd.read_csv(f'{raw_data}/gas_tax_historical/historical_gas_tax_2013.csv')
drop_states = ['Mean', 'Weighted Avg', 'Puerto Rico', 'Federal Tax']
gas_tax_historical_df = gas_tax_historical_df[~gas_tax_historical_df['State'].isin(drop_states)]
gas_tax_historical_df['GasolineEffDate'] = pd.to_datetime(gas_tax_historical_df['GasolineEffDate'])
# now i want to find and store a list of states whose effective date is before january 01, 2000
cutoff_date = pd.to_datetime('2000-01-01')
filtered_df = gas_tax_historical_df[gas_tax_historical_df['GasolineEffDate'] < cutoff_date]
states_list = filtered_df['State'].unique().tolist()
# okay so basically i don't need to worry about these variables any longer
# let's pull our next dataset
