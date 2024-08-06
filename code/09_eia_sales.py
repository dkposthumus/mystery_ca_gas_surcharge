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

variables = ['VBS', 'VDS', 'VRK', 'VTC', 'VTR', 'VWR']

# Initialize an empty list to store all the DataFrames
all_sales_df = []

# Base URL and parameters
api_url = 'https://api.eia.gov/v2/petroleum/cons/refmg/data'
params = {'api_key': 'QyPbWQo92CjndZz8conFD9wb08rBkP4jnDV02TAd'}

# Iterate through each variable
for v in variables:
    # Define the header for the API request
    header = {
        "frequency": "monthly",
        "data": [
            "value"
        ],
        "facets": {
            "duoarea": [
                "NUS",
                "SCA"
            ],
            "process": [
                v
            ],
            "product": [
                "EPM0",
                "EPM0R",
                "EPMR"
            ]
        },
        "start": "2000-01",
        "end": "2022-03",
        "sort": [
            {
                "column": "period",
                "direction": "desc"
            }
        ],
        "offset": 0,
        "length": 5000
    }
    # Make the API request
    gas_sales = requests.get(api_url, params=params, headers={'X-Params': json.dumps(header)})
    # Check if the request was successful
    if gas_sales.status_code == 200:
        gas_sales_data = gas_sales.json()
        gas_sales_series = gas_sales_data['response']['data']
        # Process the data and store in a DataFrame
        sales_values = []
        for data_point in gas_sales_series:
            date = data_point['period']
            area = data_point['area-name']
            product = data_point['product-name']
            process = data_point['process-name']
            sales = data_point['value']
            sales_values.append({
                'area': area, 
                'date': date, 
                'product type': product,
                'sales type': process, 
                'sales': sales,
            })
        sales_df = pd.DataFrame(sales_values)
        # Append the DataFrame to the list
        all_sales_df.append(sales_df)
    else:
        print(f'Failed to retrieve data for process {v}. Status code: {gas_sales.status_code}')
# Concatenate all DataFrames into a single DataFrame
sales_df = pd.concat(all_sales_df, ignore_index=True)

sales_df = sales_df.pivot(index=['date', 'area', 'sales type'], columns='product type', values='sales')
sales_df.reset_index(inplace=True)
sales_df = sales_df.pivot(index=['date', 'area'], columns='sales type', 
                          values=['Reformulated Motor Gasoline', 'Regular Gasoline', 'Total Gasoline'])
sales_df.columns = [' '.join(col).strip() for col in sales_df.columns.values]
sales_df.reset_index(inplace=True)
sales_df['date'] = pd.to_datetime(sales_df['date'])
sales_df.set_index('date', inplace=True)

strings = ['U.S.', 'CALIFORNIA']
varlist = ['Bulk Sales (Volume)', 'DTW Sales Volume',
        'Retail Sales by Refiners and Gas Plants',
        'Through Company Outlets Volume by Refiners and Gas Plants',
        'Rack Sales Volume']
typelist = ['Reformulated Motor Gasoline', 
        'Regular Gasoline', 'Total Gasoline']
# Loop through each DataFrame and corresponding string
for area in strings:
    df = sales_df[sales_df['area'] == area]
    for type in typelist:
        for var in varlist:
            df[f'{type} {var}'] = pd.to_numeric(df[f'{type} {var}'], errors='coerce')
        df[f'{type} total'] = df[[f'{type} {var}' for var in varlist]].sum(axis=1)
        for var in varlist:
            df[f'{type} {var}'] = df[f'{type} {var}'] / df[f'{type} total']
        cumulative_var1 = df[f'{type} Bulk Sales (Volume)']
        cumulative_var2 = cumulative_var1 + df[f'{type} DTW Sales Volume']
        cumulative_var3 = cumulative_var2 + df[f'{type} Rack Sales Volume']
        cumulative_var4 = cumulative_var3 + df[f'{type} Retail Sales by Refiners and Gas Plants']
        cumulative_var5 = cumulative_var4 + df[f'{type} Through Company Outlets Volume by Refiners and Gas Plants']
        #cumulative_var6 = cumulative_var4 + df[f'{type} Wholesale/Resale Volume by Refiners and Gas Plants']
        plt.figure(figsize=(10, 6))
        plt.fill_between(df.index, 0, cumulative_var1, 
                         color='skyblue', alpha=0.5, label='Bulk Sales (Volume)')
        plt.plot(df.index, cumulative_var1, color='blue', linewidth=2)
        plt.fill_between(df.index, cumulative_var1, cumulative_var2, 
                         color='lightcoral', alpha=0.5, label='DTW Sales Volume')
        plt.plot(df.index, cumulative_var2, color='red', linewidth=2)
        plt.fill_between(df.index, cumulative_var2, cumulative_var3, 
                         color='bisque', alpha=0.5, label='Rack Sales Volume')
        plt.plot(df.index, cumulative_var3, color='darkorange', linewidth=2)
        plt.fill_between(df.index, cumulative_var3, cumulative_var4, 
                         color='limegreen', alpha=0.5, label='Retail Sales by Refiners and Gas Plants')
        plt.plot(df.index, cumulative_var4, color='darkgreen', linewidth=2)
        plt.fill_between(df.index, cumulative_var4, cumulative_var5, 
                         color='darkgoldenrod', alpha=0.5, label='Through Company Outlets Volume by Refiners and Gas Plants')
        plt.plot(df.index, cumulative_var5, color='yellow', linewidth=2)
        #plt.fill_between(df.index, cumulative_var5, cumulative_var6, 
                         #color='violet', alpha=0.5, label='Wholesale/Resale Volume by Refiners and Gas Plants')
        #plt.plot(df.index, cumulative_var6, color='purple', linewidth=2)
        plt.title(f'{type} Stacked Graph, {area}')
        plt.xlabel('Date')
        plt.ylabel('Share of Gasoline Sold')
        plt.legend(loc='upper left')
        plt.grid(True)
        if type == 'Total Gasoline':
            plt.savefig(f'{output}/stacked_{area}.png')
        plt.show()

sales_df.to_csv(
    f'{data}/sales_type.csv',
    index=False,
)