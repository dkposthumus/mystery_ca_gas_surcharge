import pandas as pd
from pathlib import Path

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge-1' / 'oregon')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
code = Path.cwd() 

cfp = pd.read_excel(f'{raw_data}/cfp.xlsx', sheet_name='Monthly Credit Transfer Summary')

# first, make all columns lowercase 
cfp.columns = cfp.columns.str.lower()
# now make all string columns lowercase
cfp = cfp.apply(lambda col: col.str.lower() if col.dtype == 'object' or pd.api.types.is_string_dtype(col) else col)
# then, forward fill the year column
cfp['year'] = cfp['year'].ffill()
# now map month names to the number
month_map = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}
cfp['month'] = cfp['month'].str.lower().map(month_map)
cfp['day'] = 1
cfp['date'] = pd.to_datetime(dict(year=cfp['year'], month=cfp['month'], day=cfp['day']))

cfp.rename(
    columns = {
        'avg. price per credit': 'credit_price'
    }, inplace=True
)

# now let's calculate the cfp cost
cfp['cfp_cost'] = (
    ((98.06 - 91.68) * 11.38)
    * (cfp['credit_price'] / 1000000)
)

cfp = cfp[['date', 'cfp_cost']]

cfp.to_csv(f'{clean_data}/cfp.csv', index=False)