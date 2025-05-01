import requests
import pandas as pd
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge' / 'washington_state')
data = (work_dir / 'data')
clean_data = (data / 'clean')
code = Path.cwd() 

# I'm fetching the data using an API from EIA
# the two series I'm interested in are:
# EMM_EPM0_PTE_NUS_DPG -- US all formulations retail price
# EMM_EPM0_PTE_SCA_DPG -- CA all formulations retail price
# and i'm interested in their maximum start and end dates -- so 2000 - 2024, monthly frequency
api_url = 'https://api.eia.gov/v2/petroleum/pri/gnd/data'
params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}
header = {
    "frequency": "monthly",
    "data": [
        "value"
    ],
    "facets": {
        "duoarea": [
            "NUS",
            "R10",
            "R1X",
            "R1Y",
            "R1Z",
            "R20",
            "R30",
            "R40",
            "R5XCA",
            "SCA",
            "SCO",
            "SFL",
            "SMA",
            "SMN",
            "SNY",
            "SOH",
            "STX"
        ],
        "product": [
            "EPMR"
        ]
    },
    'start': '2005-01',
    'end': '2025-05',
    "sort": [
        {
            "column": "period",
            "direction": "desc"
        }
    ],
    "offset": 0,
    "length": 5000
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

df = gas_retail_df.copy()
df['date'] = pd.to_datetime(df['date'], format='%Y-%m')
df['gas retail price (nominal)'] = df['gas retail price (nominal)'].astype(float)

california_df = df[df['state'] == 'CALIFORNIA']
california_df.rename(
    columns = {
        'gas retail price (nominal)': 'california gas (retail) (nominal)',
    }, inplace=True
)
california_df = california_df[['date', 'california gas (retail) (nominal)']]
df = df[df['state'] != 'CALIFORNIA']
df = pd.merge(df, california_df, on='date', how='outer')
cpi = pd.read_csv(f'{clean_data}/cpi.csv')
cpi['date'] = pd.to_datetime(cpi['date'])
cpi_anchor = pd.to_datetime('2023-03-01')
fixed_cpi = cpi.loc[cpi['date'] == cpi_anchor, 'all-urban cpi'].iloc[0]
cpi['price deflator'] = cpi['all-urban cpi'] / fixed_cpi
cpi = cpi[['date', 'price deflator']]
df = pd.merge(df, cpi, on='date', how='left')

df['spread (nominal)'] = df['california gas (retail) (nominal)'] - df['gas retail price (nominal)']
df['spread (real)'] = df['spread (nominal)'] / df['price deflator']

# now let's plot all gasoline prices over time for a bunch of geographies
plt.figure(figsize=(10, 6))
for state in df['state'].unique():
    state_df = df[df['state'] == state]
    # make 12-month moving average 
    state_df['spread (nominal) ma'] = state_df['spread (nominal)'].rolling(window=12).mean()
    plt.plot(state_df['date'], state_df['spread (real)'], label=state, alpha = 0.9)

plt.axvline(pd.to_datetime('2015-02-18'), color='red', linewidth=2, 
            linestyle='--', label='Torrance Refinery Fire, Feb. 18, 2015')
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.xlabel('Date')
plt.ylabel('Spread Against California Retail Price (2023$)')
plt.title('Different Regions Spread Against California Retail Prices')

# now make plot 
plt.legend(loc='upper left')
plt.tight_layout()
plt.grid()
plt.show()