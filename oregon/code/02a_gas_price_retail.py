import requests
import pandas as pd
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge-1' / 'oregon')
data = (work_dir / 'data')
clean_data = (data / 'clean')
raw_data = (data / 'raw')

# I'm fetching the data using an API from EIA
# the two series I'm interested in are:
# EMM_EPM0_PTE_NUS_DPG -- US all formulations retail price
# EMM_EPM0_PTE_SCA_DPG -- CA all formulations retail price
# and i'm interested in their maximum start and end dates -- so 2000 - 2024, monthly frequency
api_url = 'https://api.eia.gov/v2/petroleum/pri/gnd/data'
params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}
header = {
    'frequency': 'weekly',
    'data': ['value'],
    'facets': {'series': ['EMM_EPM0_PTE_NUS_DPG']},
    'start': '2000-01',
    'end': '2025-01',
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
columns_to_convert = ['U.S.']
for col in columns_to_convert:
    gas_retail_df[col] = gas_retail_df[col].astype(float)
print(gas_retail_df.dtypes)
# finally, let's rename to make clear that these are NOMINAL
gas_retail_df.rename(
    columns={
        'U.S.': 'national gas (retail) (nominal)'
    }, inplace=True
)

gas_retail_df = gas_retail_df.reset_index(drop=True)  # if the index is redundant
gas_retail_df['date'] = pd.to_datetime(gas_retail_df['date'])

# now let's pull in the raw nevada data
or_retail = pd.read_csv(f'{raw_data}/or_opis_retail.csv')
or_retail.rename(
    columns = {
        'oregon_avg_price': 'oregon gas (retail) (nominal)',
    }, inplace=True
)
or_retail['date'] = pd.to_datetime(or_retail['date'])

gas_retail_df = pd.merge(gas_retail_df, or_retail, on='date', how='outer')

# forward fill 'nevada gas (retail) nominal'
gas_retail_df['oregon gas (retail) (nominal)'] = (
    gas_retail_df['oregon gas (retail) (nominal)'].ffill()
)

filtered_df = gas_retail_df[(gas_retail_df['date'] >= '2015-01-01') & (gas_retail_df['date'] <= '2024-08-01')]
plt.figure(figsize=(10, 6))
plt.plot(filtered_df['date'], filtered_df['oregon gas (retail) (nominal)'], 
         label='OR Retail Price',
         color='blue')
plt.plot(filtered_df['date'], filtered_df['national gas (retail) (nominal)'], 
         label='USA Retail Price',
         color='orange')
plt.title('OR vs. Rest of Country Gas Retail Prices (in $2023), 2000-2024')
plt.xlabel('Date')
plt.ylabel('Retail Gasoline Price')
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))

'''plt.axvline(pd.to_datetime('2023-09-01'), color='red', linewidth=2,
            label='September 2023')'''
plt.axhline(0, color='black', linewidth=1.5, linestyle='-', label='')

plt.legend()
plt.show()

# finally let's save as a csv
gas_retail_df.to_csv(f'{clean_data}/gas_retail.csv', index=False)
