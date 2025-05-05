import pandas as pd
from pathlib import Path


# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge' / 'washington_state')
data = (work_dir / 'data')
raw_data = (data / 'raw')
clean_data = (data / 'clean')
code = Path.cwd() 

# there is no downloadable historical dataset for the most recent auction prices under the cap-and-trade program
    # also note that the cap-and-trade program only began in 2013, so that's when data starts
# here I hard code auction prices that can be found here: 
    # https://apps.ecology.wa.gov/publications/UIPages/PublicationList.aspx?IndexTypeName=Topic&NameValue=Cap-and-Invest+%e2%80%94+Market+Reports&DocumentTypeName=Publication
# the same as Severin, I focus on the "Current Action Settlement Price" found in the above table
cax = {
    'date': [
        '02/01/2023',
        '05/01/2023',
        '08/01/2023',
        '12/01/2023',
        '03/01/2024',
        '06/01/2024',
        '09/01/2024',
        '12/01/2024',
        '03/01/2025',
    ],
    'cax price': [
        48.50,
        56.01,
        63.03,
        51.89,
        25.76,
        29.92,
        29.88,
        40.26,
        50.00,
    ]
}
# Creating DataFrame
cax_df = pd.DataFrame(cax)
# even though this is the correct data regarding CAX credits, this regulation was only enforced starting
# on January 01, 2015. So drop anny before that 
cax_df['date'] = pd.to_datetime(cax_df['date'])
cutoff_date = pd.to_datetime('2023-01-01')
cax_df = cax_df[cax_df['date'] >= cutoff_date]
# okay so the auction price is the cost per tonne of CO2e
    # Severin assumes that each gallon of e-10 ethanol gas has 0.007902 tonnes of C02e
    # thus, to find the cost per gallon I multiply the whole column by 0.007902
cax_df['cax cost'] = cax_df['cax price']*0.007902
# now i can drop the cax price to de-clutter the data
cax_df = cax_df.drop(['cax price'], axis=1)
# check the dataframe 
print(cax_df)
cax_df.to_csv(f'{clean_data}/cax.csv', index=False)