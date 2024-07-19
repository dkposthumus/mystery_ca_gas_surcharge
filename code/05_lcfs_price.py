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

# since we're NOT using an API for this data pull but a csv file, I'm defining where to find that csv file relative to the data macro set above
lcfs_price = f'{raw_data}/lcfs_credit_prices.xlsx'
# now let's define only the variables we're interested in:
columns_to_keep = ['Date (Month YR)', 'ARB Monthly Average Credit Price']
# import the csv as a pandas dataframe -- including ONLY the columns we want
lcfs_price_df = pd.read_excel(lcfs_price, usecols=columns_to_keep)
# now let's rename variables
lcfs_price_df = lcfs_price_df.rename(
    columns={
        'Date (Month YR)': 'date', 
        'ARB Monthly Average Credit Price': 'lcfs credit price'
        }
)
# now let's format the dates as date
lcfs_price_df['date'] = pd.to_datetime(lcfs_price_df['date'])
# now i want to esssentially create a list of constants
    # these constants are taken from the California Air Resources Board's LCFS calculator, found here: 
        # https://ww2.arb.ca.gov/resources/documents/lcfs-data-dashboard
gas_ci_standard = 96.50
gas_ci_max = 99.78
gas_energy_density = 119.53
ethanol_energy_density = 81.51
# now let's create a new variable, this one in terms of $/gal capturing the LCF's cost per gallon of gas
lcfs_price_df['lcfs cost'] = (-1) * ((gas_ci_standard - gas_ci_max)*(gas_energy_density)*0.9 + (gas_ci_standard-79.9)*0.1*ethanol_energy_density)*lcfs_price_df['lcfs credit price']/1000000

# the date variable is incorrect for this data; right now, instead of listing September 2017 as September 01, 2017, the date variable is listing September 17, 2017
    # first let's extract the month year, and  then remake the variable 
lcfs_price_df['year'] = pd.DatetimeIndex(lcfs_price_df['date']).year
lcfs_price_df['month'] = pd.DatetimeIndex(lcfs_price_df['date']).month
    # now set a day variable equal to 1 
lcfs_price_df['day'] = 1
# now over-write our current date variable with a date variable containing info from these 3 
lcfs_price_df['date'] = pd.to_datetime(dict(year=lcfs_price_df['year'], month=lcfs_price_df['month'], day=lcfs_price_df['day']))
# now let's drop the unnecessary lcfs price variable
lcfs_price_df = lcfs_price_df.drop(['lcfs credit price'], axis=1)
# let's check the dataset:
print(lcfs_price_df)
lcfs_price_df.to_csv(f'{data}/lcfs.csv', index=False)