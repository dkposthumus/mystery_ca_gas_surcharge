import requests
import pandas as pd
import json
from pathlib import Path
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

# to decompose the MGS i need to find the differences between CA and the rest of the country:
master_df = pd.read_csv(f'{data}/master.csv')
master_df['price difference'] = master_df['california gas (retail) (nominal)'] - master_df['national gas (retail) (nominal)']
master_df['excise tax difference'] = -1*(master_df['ca state gas tax'] - master_df['average state tax excl. ca'])
for var in ['ca state.local tax cost', 'lcfs cost', 'ust fee', 'cax cost', 'carb cost premium']:
    master_df[var] = -1*master_df[var]
master_df['unexplained differential'] = master_df['unexplained differential (nominal)']
vars_to_plot = ['price difference', 'excise tax difference', 'ca state.local tax cost',
                'lcfs cost', 'ust fee', 'cax cost', 'carb cost premium', 
                'unexplained differential']
for var in vars_to_plot:
    master_df[var] = master_df[var]/master_df['price deflator']

master_df['date'] = pd.to_datetime(master_df['date'])
cut_off_date = pd.to_datetime('2000-01-01')
master_df = master_df[master_df['date']>=cut_off_date]
master_df['4_year_period'] = (master_df['date'].dt.year // 4) * 4
# Group by the 3-year period and calculate the mean for each group
collapsed_df = master_df.groupby('4_year_period')[vars_to_plot].mean().reset_index()
collapsed_df = collapsed_df[collapsed_df['4_year_period'] != 2024]

bar_width = 0.1
index = np.arange(len(collapsed_df))
plt.figure(figsize=(14,8))
for i, var in enumerate(vars_to_plot):
    plt.bar(index + i * bar_width, collapsed_df[var], width=bar_width, label=var)

plt.xlabel('4-Year Period')
plt.ylabel('Current 2023$/Gallon')
plt.title('4-Year Period Averages for Components of the MGS')
plt.xticks(index + bar_width * (len(vars_to_plot) / 2), collapsed_df['4_year_period'])

plt.legend(title='MGS Components', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.grid(True)
plt.savefig(f'{output}/mgs_decomp.png')
plt.show()