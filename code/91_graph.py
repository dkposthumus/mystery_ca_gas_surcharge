import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import matplotlib.dates as mdates

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 

# now let's import the master dataset 
master_df = pd.read_csv(f'{data}/master.csv')
# set the index to be equal to the date variable
master_df['date'] = pd.to_datetime(master_df['date'])
master_df.set_index('date', inplace=True)

# let's start with a simple time-series of 1) explained differential and 2) unexplained differential
# Setting up the figure
plt.figure(figsize=(10, 6))
# Plotting the unexplained differential
plt.plot(master_df.index, master_df['unexplained differential (real)'], label='Unexplained Differential (Real)', color='blue')
# Plotting the explained differential
plt.plot(master_df.index, master_df['explained differential (real)'], label='Explained Differential (Real)', color='green')
# Adding titles and labels
plt.title('Time Series of Unexplained and Explained Differentials (Real)')
plt.xlabel('Date')
plt.ylabel('Differential (Real)')
# Formatting the x-axis to show only the year
ax = plt.gca()  # Get current axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_major_locator(mdates.YearLocator())
# Adding a legend
plt.legend()
# Displaying the plot
plt.show()