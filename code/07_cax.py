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

# there is no downloadable historical dataset for the most recent auction prices under the cap-and-trade program
    # also note that the cap-and-trade program only began in 2013, so that's when data starts
# here I hard code auction prices that can be found here: 
    # https://ww2.arb.ca.gov/sites/default/files/2020-08/results_summary.pdf
# the same as Severin, I focus on the "Current Action Settlement Price" found in the above table
cax = {
    'date': [
        '11/01/2024',
        '08/01/2024',
        '05/01/2024',
        '02/01/2024',
        '11/01/2023',
        '08/01/2023',
        '05/01/2023',
        '02/01/2023',
        '11/01/2022',
        '08/01/2022',
        '05/01/2022',
        '02/01/2022',
        '11/01/2021',
        '08/01/2021',
        '05/01/2021',
        '02/01/2021',
        '11/01/2020',
        '08/01/2020',
        '05/01/2020',
        '02/01/2020',
        '11/01/2019',
        '08/01/2019',
        '05/01/2019',
        '02/01/2019',
        '11/01/2018',
        '08/01/2018',
        '05/01/2018',
        '02/01/2018',
        '11/01/2017',
        '08/01/2017',
        '05/01/2017',
        '02/01/2017',
        '11/01/2016',
        '08/01/2016',
        '05/01/2016',
        '02/01/2016',
        '11/01/2015',
        '08/01/2015',
        '05/01/2015',
        '02/01/2015',
        '11/01/2014',
        '08/01/2014',
        '05/01/2014',
        '02/01/2014',
        '11/01/2013',
        '08/01/2013',
        '05/01/2013',
        '02/01/2013',
        '11/01/2012',
    ],
    'cax price': [
        31.91,
        30.24,
        37.02,
        41.76,
        38.73,
        35.20,
        30.33,
        27.85,
        26.80,
        27.00,
        30.85,
        29.15,
        28.26,
        23.30,
        18.80,
        17.80,
        16.93,
        16.68,
        16.68,
        17.87,
        17.00,
        17.16,
        17.45,
        15.73,
        15.31,
        15.05,
        14.65,
        14.61,
        15.06,
        14.75,
        13.80,
        13.57,
        12.73,
        12.73,
        12.73,
        12.73,
        12.73,
        12.52,
        12.29,
        12.21,
        12.10,
        11.50,
        11.50,
        11.48,
        11.48,
        12.22,
        14.00,
        13.62,
        10.09,
    ]
}
# Creating DataFrame
cax_df = pd.DataFrame(cax)
# even though this is the correct data regarding CAX credits, this regulation was only enforced starting
# on January 01, 2015. So drop anny before that 
cax_df['date'] = pd.to_datetime(cax_df['date'])
cutoff_date = pd.to_datetime('2015-01-01')
cax_df = cax_df[cax_df['date'] >= cutoff_date]
# okay so the auction price is the cost per tonne of CO2e
    # Severin assumes that each gallon of e-10 ethanol gas has 0.007902 tonnes of C02e
    # thus, to find the cost per gallon I multiply the whole column by 0.007902
cax_df['cax cost'] = cax_df['cax price']*0.007902
# now i can drop the cax price to de-clutter the data
cax_df = cax_df.drop(['cax price'], axis=1)
# check the dataframe 
print(cax_df)
cax_df.to_csv(f'{data}/cax.csv', index=False)