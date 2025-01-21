import requests
import json
import pandas as pd
from pathlib import Path
# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 

# define function for fetching cpi data via API
def fetch_cpi_data(start_year, end_year):
    headers = {'Content-type': 'application/json'}
    # I want the all-urban CPI, whose series ID is 'CUUR0000SA0'
    data = json.dumps(
        {'seriesid': ['CUUR0000SA0'], 'startyear': start_year, 'endyear': end_year}
    )
    p = requests.post(
        'https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers
    )
    json_data = json.loads(p.text)
    return json_data['Results']['series']

# Combine data from three separate API requests
# this is necessary because BLS's API requests are limited to 10 years each, but i want 2000-2024
# first create empty list of all series of interest, and then append each API request onto that list
cpi_all_series = []
# define the data fetching process for the 3 separate intervals using function defined earlier
for start_year in range(2000, 2025, 10):
    end_year = min(start_year + 9, 2025)
    series_data = fetch_cpi_data(str(start_year), str(end_year))
    cpi_all_series.extend(series_data)

# extract data from API response
# start with empty list that we'll append on through our loop
cpi_data_rows = []
# now for each datapoint run the loop defining 3 variables: year, month, and value for CPI
for series in cpi_all_series:
    seriesId = series['seriesID']
    for item in series['data']:
        year = item['year']
        month = item['period']
        cpi = item['value']
        # append the output from each iteration to the empty cpi list created earlier
        cpi_data_rows.append({'year': year, 'month': month, 'all-urban cpi': cpi})
# create Pandas DataFrame from the cpi data extracted in above loop
cpi_df = pd.DataFrame(cpi_data_rows)
# now I want to make a datetime variable, combining month and year
cpi_df['date'] = pd.to_datetime(
    cpi_df['year'].astype(str) + '-' + cpi_df['month'].str[1:]
)
# now let's set the date variable as the index
cpi_df.set_index('date')
# and drop the unnecessary variables -- i no longer need year nor month, since i have a date variable containing information from both variables
cpi_df = cpi_df.drop(['year', 'month'], axis=1)
# now let's check the dataframe
print(cpi_df)
print(cpi_df.columns)
# finally let's save as a csv
cpi_df.to_csv(
    f'{data}/cpi.csv', index=False
)
