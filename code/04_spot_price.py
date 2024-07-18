import requests
import pandas as pd
import json

data_path = '/Users/danpost/Dropbox/Myster_Gas_Surcharge/Analysis/Data'
# I'm fetching the data using an API from EIA
api_url = 'https://api.eia.gov/v2/petroleum/pri/spt/data'
params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}
header = {
    'frequency': 'monthly',
    'data': ['value'],
    'facets': {
        'series': [
            'EER_EPMRR_PF4_Y05LA_DPG',
            'EER_EPMRU_PF4_RGC_DPG',
            'EER_EPMRU_PF4_Y35NY_DPG',
            'RBRTE',
        ]
    },
    'start': '2000-01',
    'end': '2024-07',
    'sort': [{'column': 'period', 'direction': 'asc'}],
    'offset': 0,
    'length': 5000,
}
# now let's actually request and get the data:
spot_prices = requests.get(
    api_url, params=params, headers={'X-Params': json.dumps(header)}
)

# Check if request was successful
if spot_prices.status_code == 200:
    spot_prices_data = spot_prices.json()
    # output_file = f'{data_path}/file.json'
    # with open(output_file, 'w', encoding='utf-8') as f:
    # json.dump(spot_prices_data, f, ensure_ascii=False, indent=4)
    # Extract data from JSON structure
    spot_price_series = spot_prices_data['response']['data']
    # print(data_series)
    spot_data_values = []
    for data_point in spot_price_series:
        date = data_point['period']
        # var_descr = data_point['series-description']
        var = data_point['series']
        spot_price_nom = data_point['value']
        spot_data_values.append(
            {'variable': var, 'date': date, 'spot price (nominal)': spot_price_nom}
        )
    # Create Pandas DataFrame
    spot_prices_df = pd.DataFrame(spot_data_values)
    # Display DataFrame
    print(spot_prices_df.head())
else:
    print(f'Failed to retrieve data. Status code: {spot_prices.status_code}')
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
]
for col in columns_to_convert:
    spot_prices_df[col] = spot_prices_df[col].astype(float)
print(spot_prices_df.dtypes)
# before proceeding, we have to convert the europe brent spot price into $/Gal
# right now, it's in $/Barrel and there are 42 gallons per barrel, so we're just going to divide
spot_prices_df['RBRTE'] = spot_prices_df['RBRTE'] / 42
# now let's rename our variables to something more intuitive -- noting these are all nominal
spot_prices_df = spot_prices_df.rename(
    columns={
        'RBRTE': 'uk brent (nominal)',
        'EER_EPMRU_PF4_RGC_DPG': 'gulf spot price (nominal)',
        'EER_EPMRU_PF4_Y35NY_DPG': 'ny spot price (nominal)',
        'EER_EPMRR_PF4_Y05LA_DPG': 'la spot price (nominal)',
    }
)
print(spot_prices_df)
# finally let's save as a csv
spot_prices_df.to_csv(
    '/Users/danpost/Dropbox/Myster_Gas_Surcharge/Analysis/Data/spot_prices.csv',
    index=False,
)
