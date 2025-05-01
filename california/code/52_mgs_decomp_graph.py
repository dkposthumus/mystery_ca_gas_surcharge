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
master_df['price difference'] = master_df['california gas (retail) (nominal)'] - master_df['national retail excl. ca (nominal)']
master_df['excise tax difference'] = (master_df['ca state gas tax'] - master_df['average state tax excl. ca'])
master_df['unexplained differential'] = master_df['unexplained differential (nominal)']/master_df['price deflator']
vars_to_plot = ['price difference', 'excise tax difference', 'ca state.local tax cost',
                'lcfs cost', 'ust fee', 'cax cost', 'carb cost premium']
for var in vars_to_plot:
    master_df[var] = master_df[var]/master_df['price deflator']

master_df['date'] = pd.to_datetime(master_df['date'])
cut_off_date = pd.to_datetime('2000-01-01')
master_df = master_df[master_df['date']>=cut_off_date]
master_df.set_index('date', inplace=True)
master_df['year'] = master_df.index.year
annual_df = master_df.groupby('year').mean()

# Define variables to plot
vars_to_plot = ['excise tax difference', 'ca state.local tax cost', 'lcfs cost',
                'ust fee', 'cax cost', 'carb cost premium']
positive_vars = annual_df[vars_to_plot].clip(lower=0)
negative_vars = annual_df[vars_to_plot].clip(upper=0)

fig, ax = plt.subplots(figsize=(14, 7))

bar_width = 0.35
years = annual_df.index
ax.bar(years - bar_width/2, annual_df['price difference'], 
       width=bar_width, color='blue', label='Price Difference')
bottom = np.zeros(len(annual_df))
colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#C2C2C2', '#FFB266']
for i, var in enumerate(vars_to_plot):
    ax.bar(years + bar_width/2, positive_vars[var],
           bottom=bottom, width=bar_width, label=var, color=colors[i])
    bottom += positive_vars[var]
bottom = np.zeros(len(annual_df))
for i, var in enumerate(vars_to_plot):
    ax.bar(years + bar_width/2, negative_vars[var], 
           bottom=bottom, width=bar_width, color=colors[i])
    bottom += negative_vars[var]
ax.plot(annual_df.index, annual_df['unexplained differential'], 
        color='purple', linewidth=5, label='Unexplained Differential', marker='o')
plt.axvline(x=2015, 
            color='red', linewidth=2, linestyle='--', 
            label='Torrance Refinery Fire, Feb. 18, 2015')
ax.set_title('Comparison of Price Difference and Other Components with Unexplained Differential')
ax.set_xlabel('Year')
ax.set_ylabel('Value')
ax.axhline(0, color='black', linewidth=2)
ax.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)
plt.xticks(ticks=years, labels=years, rotation=45)
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
plt.savefig(f'{output}/mgs_decomp_v1.png', bbox_inches='tight')
plt.show()

# now let's do the same plot, but super-imposing the costs/tax differences on the price difference
vars_to_plot = ['excise tax difference', 'ca state.local tax cost', 'lcfs cost',
                'ust fee', 'cax cost', 'carb cost premium']
fig, ax = plt.subplots(figsize=(14, 7))
bar_width = 0.35
years = annual_df.index
ax.bar(years, annual_df['price difference'], width=bar_width, color='blue', label='Price Difference')
colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#C2C2C2', '#FFB266']
bottom = np.zeros(len(annual_df))
for i, var in enumerate(vars_to_plot):
    ax.bar(years, annual_df[var], bottom=bottom, 
           width=bar_width, label=var, color=colors[i], alpha=0.5)
    bottom += annual_df[var]  # Update bottom to stack the bars
ax.plot(annual_df.index, annual_df['unexplained differential'], 
        color='purple', linewidth=5, label='Unexplained Differential', marker='o')
plt.axvline(x=2015, 
            color='red', linewidth=2, linestyle='--', 
            label='Torrance Refinery Fire, Feb. 18, 2015')
ax.set_title('Superimposed Components on Price Difference with Unexplained Differential')
ax.set_xlabel('Year')
ax.set_ylabel('Value')
ax.axhline(0, color='black', linewidth=2)
ax.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)
plt.xticks(ticks=years, labels=years, rotation=45)
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
plt.savefig(f'{output}/mgs_decomp_v2.png', bbox_inches='tight')
plt.show()