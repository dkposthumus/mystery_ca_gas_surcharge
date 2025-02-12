import pandas as pd
from pathlib import Path
from typing import List, Tuple
import numpy as np
import osmnx as ox
import networkx as nx
from collections import defaultdict
from math import radians, sin, cos, sqrt, atan2
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
zcta_raw = (raw_data / 'zcta_pops')
code = Path.cwd() 
output = (work_dir / 'output')

# let's read in the zcta population data
pop_data = {}
for year in ['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020',
             '2021', '2022', '2023']:
    df = pd.read_csv(zcta_raw / f'ACSDP5Y{year}.DP05-Data.csv', header=1)
    # first, restrict observations to to those swhose value for the 'Geographic Area Name' column contains 'ZCTA5'
    df = df[df['Geographic Area Name'].str.contains('ZCTA5')]
    print(df['Geographic Area Name'].unique())
    # then create a 'zcta' column which is equal to all characters after 'ZCTA5' in the 'Geographic Area Name' column
    df['zcta'] = df['Geographic Area Name'].str.extract(r'ZCTA5\s*(\d+)')
    # rename total population variable 
    df.rename(columns={'Estimate!!SEX AND AGE!!Total population': 'total pop.'}, inplace=True)
    # then, keep only the total population variable and zcta variables
    df = df[['zcta', 'total pop.']]
    df['year'] = year
    # now let's append all of the dataframes so that we have a panel dataset of zcta populations by year
    pop_data[year] = df
    
pop_data = pd.concat(pop_data.values())

pop_data['zcta'] = pop_data['zcta'].astype(int)

# what we really want, however, is population on the zip, not zcta level 
zcta_zip_crosswalk = pd.read_csv(f'{raw_data}/zip_zcta_xref.csv')
print(zcta_zip_crosswalk.columns)

# now create crosswalk from zcta to zip 
zcta_zip_crosswalk = zcta_zip_crosswalk[['zcta', 'zip_code']]
zcta_zip_crosswalk.rename(columns={'zip_code': 'zip'}, inplace=True)
pop_data = pop_data.merge(zcta_zip_crosswalk, on='zcta', how='left')

pop_data = pop_data[['year', 'zip', 'total pop.']]

pop_data.to_csv(data / 'zip_pops.csv', index=False)