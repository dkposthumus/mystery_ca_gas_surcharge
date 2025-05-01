import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

# let's hard code the tables from this website (code generated using chat gpt): 
# https://nepis.epa.gov/Exe/ZyPDF.cgi?Dockey=P100T5J6.pdf
summer_gasoline_properties = {
    'Property': ['Sulfur (ppm)', 'Benzene (vol%)', 'RVP (psi)', 'Aromatics (vol%)', 'E200 (vol%)', 'E300 (vol%)', 'Olefins (vol%)', 'Ethanol (vol%)'],
    '1990 Baseline': [339, 1.53, 8.7, 32, 41, 83, 13.1, 0.6],
    '2000 RFG Average': [126, 0.59, 6.78, 19.3, 47.6, 84.7, 10.6, 1.14],
    '2000 CG Average': [324, 1.15, 8.27, 28.5, 45.2, 80.7, 11.8, 0.84],
    '2016 RFG Average': [23.1, 0.51, 7.1, 17.12, 47.9, 85.6, 10.5, 9.61],
    '2016 RFG 95%': [48.2, 0.86, 7.47, 27.3, 54.8, 92.0, 18.7, 9.97],
    '2016 CG Average': [22.5, 0.63, 9.08, 21.76, 53.0, 84.8, 8.38, 9.28],
    '2016 CG 95%': [51.0, 1.27, 10.0, 32.1, 61.4, 91.1, 16.4, 9.8]
}
summer_gasoline_properties_df = pd.DataFrame(summer_gasoline_properties)

winter_gasoline_properties = {
    'Property': ['Sulfur (ppm)', 'Benzene (vol%)', 'RVP (psi)', 'Aromatics (vol%)', 'E200 (vol%)', 'E300 (vol%)', 'Olefins (vol%)', 'Ethanol (vol%)'],
    '1990 Baseline': [339, 1.64, 11.5, 26.4, 50, 83, 11.9, 0.6],
    '2000 RFG Average': [200, 0.65, 12.1, 19, 56.3, 86.1, 11.8, 1.22],
    '2000 CG Average': [293, 1.08, 12.1, 24.8, 50.4, 83.4, 12, 1.19],
    '2016 RFG Average': [24.4, 0.51, 13.1, 16.4, 58.1, 87.0, 9.16, 9.7],
    '2016 RFG 95%': [48, 0.84, 14.9, 25.1, 62.5, 92.7, 18.8, 10.1],
    '2016 CG Average': [23.0, 0.58, 12.6, 18.8, 56.2, 86.6, 8.12, 9.28],
    '2016 CG 95%': [55.0, 1.13, 15.0, 28.7, 62.8, 93.0, 17.0, 9.8]
}
winter_gasoline_properties_df = pd.DataFrame(winter_gasoline_properties)

properties_over_time = {
    'year': [1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
    'Volume': [107220, 112950, 114776, 115574, 117153, 120802, 121617, 122166, 119666, 123178, 122403, 114032, 115404, 116286, 121131, 119696, 119689, 123005, 125386, 125000],
    'Oxygen': [0.72, 1.05, 1.08, 1.07, 1.07, 1.08, 1.17, 1.39, 1.38, 1.19, 1.27, 2.02, 2.62, 3.13, 3.13, 3.24, 3.33, 3.34, 3.43, 3.48],
    'API Gravity': [60.0, 60.0, 60.0, 60.0, 59.6, 59.8, 59.4, 60.1, 60.3, 60.1, 60.2, 60.8, 60.3, 60.4, 60.7, 61.0, 61.3, 61.4, 0, 0],
    'Ethanol': [0.31, 0.80, 0.97, 1.07, 1.05, 1.14, 1.33, 2.02, 2.23, 2.91, 3.44, 5.54, 7.20, 8.65, 8.72, 9.01, 9.21, 9.23, 9.38, 9.57],
    'MTBE': [2.89, 3.65, 3.45, 3.27, 3.36, 3.27, 3.43, 3.35, 2.89, 0.64, 0.02, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'TAME': [0.22, 0.36, 0.29, 0.35, 0.37, 0.39, 0.30, 0.24, 0.23, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
    'Sulfur': [312.6, 272.7, 283.8, 270.2, 264.1, 259.4, 243.8, 112.0, 94.8, 49.2, 39.9, 34.2, 33.3, 32.4, 30.0, 29.4, 27.2, 25.3, 23.4, 23.1],
    'Aromatics': [24.7, 24.8, 24.8, 24.6, 24.9, 24.7, 24.7, 24.5, 24.5, 24.7, 24.4, 22.5, 22.0, 21.2, 20.2, 19.6, 19.1, 18.8, 19.0, 19.3],
    'Olefins': [12.2, 11.2, 11.5, 11.7, 12.5, 11.7, 11.6, 11.3, 11.7, 11.1, 11.2, 10.5, 10.3, 10.0, 9.8, 9.6, 9.5, 9.3, 9.0, 8.6],
    'Benzene': [1.01, 1.00, 1.00, 0.99, 1.02, 0.97, 1.00, 0.98, 1.04, 1.04, 1.04, 1.02, 0.97, 0.89, 0.70, 0.63, 0.59, 0.59, 0.58, 0.58],
    'RVP': [10.34, 10.35, 10.33, 10.23, 10.17, 10.16, 10.20, 10.21, 10.18, 10.15, 10.20, 10.33, 10.47, 10.54, 10.64, 10.73, 10.82, 10.95, 10.83, 10.60],
    'E200 Vol%': [49.3, 49.0, 49.1, 49.2, 48.9, 48.9, 49.0, 49.3, 49.7, 49.1, 49.6, 52.0, 52.7, 53.8, 54.7, 55.2, 55.7, 55.6, 55.0, 54.4],
    'E300 Vol%': [82.5, 82.6, 82.6, 83.0, 83.0, 82.8, 82.6, 82.7, 83.4, 83.7, 83.8, 85.8, 84.8, 85.3, 86.0, 86.3, 86.9, 87.0, 86.6, 85.9],
    'T50': [201.5, 202.0, 201.9, 201.7, 203.5, 203.5, 202.8, 202.3, 201.2, None, None, None, None, None, None, None, None, None, None, None],
    'T90': [331.4, 329.5, 330.2, 327.8, 327.9, 329.1, 330.6, 330.0, 326.9, None, None, None, None, None, None, None, None, None, None, None]
}
properties_over_time_df = pd.DataFrame(properties_over_time)

# hard-coding a time series of california regulations 
years = list(range(1996, 2024))  
carfg_standards = {
    'year': years,
    'CARFG Phase': ['CARFG2' if year <= 2002 else 'CARFG3' for year in years],
    'CARFG RVP': [7 if year <= 2002 else 6.9 for year in years],
    'CARFG Sulfur': [40 if year <= 2002 else 20 for year in years],
    'CARFG Benzene': [1.00 if year <= 2002 else 0.8 for year in years],
    'CARFG Aromatics': [25.0] * len(years), 
    'CARFG Olefins': [6.0] * len(years),   
    'CARFG T50': [210 if year <= 2002 else 213 for year in years],
    'CARFG T90': [300 if year <= 2002 else 305 for year in years],
    'CARFG Oxygen': [2.0] * len(years)
}
# Creating the DataFrame
carfg_standards_df = pd.DataFrame(carfg_standards)

file_path = data / 'fuel_characteristics.xlsx'
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    summer_gasoline_properties_df.to_excel(writer, 
                sheet_name='summer_gasoline_properties', index=False) 
    winter_gasoline_properties_df.to_excel(writer, 
                sheet_name='winter_gasoline_properties', index=False)
    properties_over_time_df.to_excel(writer,
                sheet_name='properties_over_time', index=False)
    carfg_standards_df.to_excel(writer,
                sheet_name='carfg_standards', index=False)


# now let's plot these over time
carfg2_data = carfg_standards_df[carfg_standards_df['CARFG Phase'] == 'CARFG2']
carfg3_data = carfg_standards_df[carfg_standards_df['CARFG Phase'] == 'CARFG3']

num_vars = len(vars) 
ncols = 2  
nrows = (num_vars + 1) // ncols  

fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, nrows * 5))
axs = axs.flatten()
vars = ['RVP', 'Sulfur', 'Benzene', 'Aromatics', 'Olefins',
            'T50', 'T90', 'Oxygen']
units = ['psi', 'ppm', 'vol%', 'vol%', 'vol%', 'F', 'F', 'vol%']
for i, (var, unit) in enumerate(zip(vars, units)):
    axs[i].plot(carfg2_data['year'], carfg2_data[f'CARFG {var}'], 
                label='CARFG2 Requirement', color='blue')
    axs[i].plot(carfg3_data['year'], carfg3_data[f'CARFG {var}'], 
                label='CARFG3 Requirement', color='green')
    axs[i].plot(properties_over_time_df['year'], properties_over_time_df[var], 
                label='National Fuel Average', color='black')
    axs[i].axvline(x=2002, color='red', linestyle='--', label='CARFG Phase Change')
    axs[i].set_title(f'{var}, CARFG Standards vs. National Fuel Averages')
    axs[i].set_xlabel('Year')
    axs[i].set_ylabel(unit)
    axs[i].legend(loc='upper left')
plt.tight_layout()
plt.savefig(f'{output}/carfg_vs_national_averages.png')
plt.show()