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
data_frames = []
spt_vars = ['EER_EPMRR_PF4_Y05LA_DPG',
            'EER_EPMRU_PF4_RGC_DPG',
            'EER_EPMRU_PF4_Y35NY_DPG',
            'RBRTE']
rac2_vars = ['R0050____3']
urls = ['spt', 'rac2']
for vars, url in zip([spt_vars, rac2_vars], urls):
    api_url = f'https://api.eia.gov/v2/petroleum/pri/{url}/data'
    params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}
    header = {
        'frequency': 'monthly',
        'data': ['value'],
        'facets': {
            'series': [
                vars
            ]
        },
        'start': '2000-01',
        'end': '2024-10',
        'sort': [{'column': 'period', 'direction': 'asc'}],
        'offset': 0,
        'length': 5000,
    }
    try:
        response = requests.get(api_url, params, headers={'X-Params': json.dumps(header)})
        response.raise_for_status() 
        spot_prices_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {api_url}: {e}")
        continue 
    try:
        spot_price_series = spot_prices_data['response']['data']
        spot_data_values = [
            {
                'variable': data_point['series'],
                'date': data_point['period'],
                'spot price (nominal)': data_point['value']
            }
            for data_point in spot_price_series
        ]
        df = pd.DataFrame(spot_data_values)
        data_frames.append(df) 
    except KeyError as e:
        print(f"Error parsing JSON data: {e}")
        continue
if data_frames:
    spot_prices_df = pd.concat(data_frames, ignore_index=True)
# okay first let's make each the date variable datetime format
spot_prices_df['date'] = pd.to_datetime(spot_prices_df['date'])
# now I need to reshape the data
spot_prices_df = spot_prices_df.pivot(
    index='date', columns='variable', values='spot price (nominal)'
).reset_index()
print(spot_prices_df)
# I need to make both the US and CA float-type variables
columns_to_convert = [
    'EER_EPMRR_PF4_Y05LA_DPG',
    'EER_EPMRU_PF4_RGC_DPG',
    'EER_EPMRU_PF4_Y35NY_DPG',
    'RBRTE',
    'R0050____3'
]
for col in columns_to_convert:
    spot_prices_df[col] = spot_prices_df[col].astype(float)
print(spot_prices_df.dtypes)
# before proceeding, we have to convert the europe brent spot price into $/Gal
# right now, it's in $/Barrel and there are 42 gallons per barrel, so we're just going to divide
for bbl_var in ['RBRTE', 'R0050____3']:
    spot_prices_df[bbl_var] = spot_prices_df[bbl_var] / 42

# now let's also pull the refiner acqusition cost for PADD5 using EIA API


# now let's rename our variables to something more intuitive -- noting these are all nominal
spot_prices_df = spot_prices_df.rename(
    columns={
        'RBRTE': 'uk brent (nominal)',
        'EER_EPMRU_PF4_RGC_DPG': 'gulf spot price (nominal)',
        'EER_EPMRU_PF4_Y35NY_DPG': 'ny spot price (nominal)',
        'EER_EPMRR_PF4_Y05LA_DPG': 'la spot price (nominal)',
        'R0050____3': 'padd5 crude refiner acquisition cost (nominal)'
    }
)
print(spot_prices_df)

# finally let's save as a csv
spot_prices_df.to_csv(
    f'{data}/spot_prices.csv',
    index=False,
)