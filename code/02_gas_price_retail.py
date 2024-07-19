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

# I'm fetching the data using an API from EIA
# the two series I'm interested in are:
# EMM_EPM0_PTE_NUS_DPG -- US all formulations retail price
# EMM_EPM0_PTE_SCA_DPG -- CA all formulations retail price
# and i'm interested in their maximum start and end dates -- so 2000 - 2024, monthly frequency
api_url = 'https://api.eia.gov/v2/petroleum/pri/gnd/data'
params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}
header = {
    'frequency': 'monthly',
    'data': ['value'],
    'facets': {'series': ['EMM_EPM0_PTE_NUS_DPG', 'EMM_EPM0_PTE_SCA_DPG']},
    'start': '2000-01',
    'end': '2024-07',
    'sort': [{'column': 'period', 'direction': 'asc'}],
    'offset': 0,
    'length': 5000,
}
# now let's actually request and get the data:
gas_retail = requests.get(
    api_url, params=params, headers={'X-Params': json.dumps(header)}
)
# Check if request was successful (if it is successful, then status code is 200)
if gas_retail.status_code == 200:
    gas_retail_data = gas_retail.json()
    # Extract data from JSON structure
    gas_retail_series = gas_retail_data['response']['data']
    # create empty list into which I'll fill
    gas_retail_values = []
    for data_point in gas_retail_series:
        date = data_point['period']
        state = data_point['area-name']
        retail_price_nom = data_point['value']
        gas_retail_values.append(
            {
                'state': state,
                'date': date,
                'gas retail price (nominal)': retail_price_nom,
            }
        )
    # Create Pandas DataFrame
    gas_retail_df = pd.DataFrame(gas_retail_values)
    # Display DataFrame
    print(gas_retail_df)
else:
    print(f'Failed to retrieve data. Status code: {gas_retail.status_code}')
# now I need to reshape the data
gas_retail_df = gas_retail_df.pivot(
    index='date', columns='state', values='gas retail price (nominal)'
).reset_index()
print(gas_retail_df.dtypes)
# okay, so I need to make both the US and CA float-type variables
columns_to_convert = ['CALIFORNIA', 'U.S.']
for col in columns_to_convert:
    gas_retail_df[col] = gas_retail_df[col].astype(float)
print(gas_retail_df.dtypes)
# finally, let's rename to make clear that these are NOMINAL
gas_retail_df = gas_retail_df.rename(
    columns={
        'CALIFORNIA': 'california gas (retail) (nominal)',
        'U.S.': 'national gas (retail) (nominal)',
        'US excl. CA': 'national excluding CA gas (retail) (nominal)',
    }
)
# let's make each the date variable datetime format
gas_retail_df['date'] = pd.to_datetime(gas_retail_df['date'])
# now let's set the date variable as the index
gas_retail_df.set_index('date')
print(gas_retail_df)
print(gas_retail_df.columns)
# finally let's save as a csv
gas_retail_df.to_csv(f'{data}/gas_retail.csv', index=False)
