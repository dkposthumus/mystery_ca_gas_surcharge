import pandas as pd
from pathlib import Path
from datetime import datetime

# let's create a set of locals referring to our directory and working directory 
home_dir = Path.home()
work_dir = (home_dir / 'mystery_ca_gas_surcharge')
data = (work_dir / 'data')
raw_data = (data / 'raw')
code = Path.cwd() 
output = (work_dir / 'output')

rack_prices_df = pd.read_excel(f'{raw_data}/bloomberg_rack_prices.xlsx', 
                               sheet_name='ca_rack_import')
rack_prices_df.rename(
    columns={
        'Date': 'date', 
        'RACKM0G PO6 R Index': 'los angeles rack price',
        'RACKK0G PO6 R Index': 'fresno rack price',   
        'RACKE0G PO6 R Index': 'bakersfield rack price',
        'RACKF0G PO6 R Index': 'barstow rack price',
        'RACKH0G PO6 R Index': 'chico rack price',
        'RACKI0G PO6 R Index': 'colton rack price',
        'RACKL0G PO6 R Index': 'imperial rack price',
        'RACKN0G PO6 R Index': 'sacramento rack price',
        'RACKO0G PO6 R Index': 'san diego rack price',
        'RACKP0G PO6 R Index': 'san francisco rack price',
        'RACKQ0G PO6 R Index': 'san jose rack price',
        'RACKR0G PO6 R Index': 'stockton rack price',
    }, 
    inplace=True
)
rack_prices_df['date'] = pd.to_datetime(rack_prices_df['date'])

rack_prices_df = (rack_prices_df.groupby(pd.Grouper(key='date', freq='MS'))
                          .agg('mean').reset_index())

rack_prices_df.to_csv(f'{data}/rack_prices.csv', index=False)

for net_gross, net_gross_letter in zip(['gross', 'net'], ['G', 'N']):
    # bakersfield detailed rack price data 
    def extract_data(city):
        df = pd.read_excel(f'{raw_data}/bloomberg_detailed_rack_{net_gross}_values.xlsx', sheet_name=f'{city}_import')
        return df
    bakersfield_df = extract_data('bakersfield')
    los_angeles_df = extract_data('los angeles')
    fresno_df = extract_data('fresno')
    barstow_df = extract_data('barstow')
    chico_df = extract_data('chico')
    colton_df = extract_data('colton')
    imperial_df = extract_data('imperial')
    sacramento_df = extract_data('sacramento')
    san_diego_df = extract_data('san diego')
    san_francisco_df = extract_data('san francisco')
    san_jose_df = extract_data('san jose')
    stockton_df = extract_data('stockton')

    dfs = [los_angeles_df, fresno_df, barstow_df, chico_df, colton_df, imperial_df, 
       sacramento_df, san_diego_df, san_francisco_df, san_jose_df, stockton_df, 
       bakersfield_df]

    for df, city, code in zip(dfs, 
                    ['los angeles', 'fresno', 'barstow', 'chico', 'colton', 'imperial', 
                     'sacramento', 'san diego', 'san francisco', 'san jose', 'stockton',
                     'bakersfield'],
                     [f'RACKM0{net_gross_letter}', f'RACKK0{net_gross_letter}', f'RACKF0{net_gross_letter}', 
                      f'RACKH0{net_gross_letter}', f'RACKI0{net_gross_letter}', f'RACKL0{net_gross_letter}',
                      f'RACKN0{net_gross_letter}', f'RACKO0{net_gross_letter}', f'RACKP0{net_gross_letter}', 
                      f'RACKQ0{net_gross_letter}', f'RACKR0{net_gross_letter}', f'RACKE0{net_gross_letter}']):
        df['date'] = pd.to_datetime(df['date'])
        # this is the overall index, capturing the totality of rack prices for {city}
        df.rename(columns={f'{code} PO6 R Index': f'dtn {net_gross} price (nominal), , , , , {city}'}, inplace=True)
        # i want to calculate the spread for a variety of variables, the list of which EXCLUDES 
        # the overall rack price and date. I am dropping the suffix 'index' from the variable names to keep clean variable names
        vars_to_calc_spread_for = list(set(
            [col.replace(' Index', '') for col in df.columns if col not in ['date', f'dtn {net_gross} price (nominal), , , , , {city}']]
        ))
        for var in vars_to_calc_spread_for:
            df[f'{var} dtn {net_gross} spread (nominal)'] = (df[f'{var} Index'] - df[f'dtn {net_gross} price (nominal), , , , , {city}'])
            df.rename(columns={f'{var} Index': f'{var} dtn {net_gross} price (nominal)'}, inplace=True)

        for spec in [f'dtn {net_gross} spread (nominal)', f'dtn {net_gross} price (nominal)']:
            df.rename(columns = {f'{code} PO6 U {net_gross}': f'{net_gross}, , unbranded, , , {city}',
                         f'{code} PO6 B {net_gross}': f'{net_gross}, , branded, , , {city}'}, inplace=True)
    # now unfortunately we have to rename manually the rest of the columns
    # the naming convention I follow is as follows: 
    # {spec}, {refiner}, branded/unbranded/ , {location of refiner}, {distributor}, {rack fuel location}
        # note that if {destination} is missing, then it is assumed to be same as {city}
    # note that for each city's dataframe i also reshape wide, 
    # so that i am concatenating each dataframe by the end of this
    def reshape_wide_to_long(df):
        # First, melt the DataFrame to long format
        df_long = pd.melt(df, id_vars=['date'], var_name='variable', value_name='value')
        variable_parts = df_long['variable'].str.split(', ', expand=True)
        df_long['spec'] = variable_parts[0]
        df_long['company'] = variable_parts[1]
        df_long['branded_indicator'] = variable_parts[2]
        df_long['location of refiner'] = variable_parts[3]
        df_long['distributor'] = variable_parts[4]
        df_long['city'] = variable_parts[5]
        df_wide = df_long.pivot_table(index=['date', 'company', 'branded_indicator', 
                                         'location of refiner', 'distributor', 
                                         'city'], 
                                  columns='spec', 
                                  values='value').reset_index()
        return df_wide

    for spec in [f'dtn {net_gross} spread (nominal)', f'dtn {net_gross} price (nominal)']:
        bakersfield_df.rename(columns = {
            f'RACKE0{net_gross_letter} PO6 S26 T1 {spec}': f'{spec}, texaco, branded, , kern, bakersfield', 
            f'RACKE0{net_gross_letter} PO6 SA3 T1 {spec}': f'{spec}, chevron, branded, , kern, bakersfield', 
            f'RACKE0{net_gross_letter} PO6 SR5 T1 {spec}': f'{spec}, shell, branded, , kern, bakersfield', 
            f'RACKE0{net_gross_letter} PO6 SX3 T1 {spec}': f'{spec}, exxon, branded, , kern, bakersfield'
            }, inplace=True)
        # there's a random duplicate variable for los angeles that we can drop now
        los_angeles_df.drop(columns=[f'RACKM0{net_gross_letter} PO6 SK8 T19 {spec}'], inplace=True)
        los_angeles_df.rename(columns={
            f'RACKM0{net_gross_letter} PO6 SSG T12 {spec}': f'{spec}, toledo refining, , orange, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 S43 T9 {spec}': f'{spec}, bp products, unbranded, carson, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SA3 T6 {spec}': f'{spec}, chevron, branded, huntington beach, chevron, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SA3 T7 {spec}': f'{spec}, chevron, branded, montebello, chevron, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SA3 T8 {spec}': f'{spec}, chevron, branded, van nuys, chevron, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SIA T25 {spec}': f'{spec}, conocophillips, branded, , phillips 66, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SK8 T12 {spec}': f'{spec}, valero, branded, orange, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SK8 T19 {spec}': f'{spec}, valero, branded, orange, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SK8 T9 {spec}': f'{spec}, valero, branded, carson, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SL6 T12 {spec}': f'{spec}, valero, unbranded, orange, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SL6 T18 {spec}': f'{spec}, valero, unbranded, signal hill, shell oil, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SL6 T19 {spec}': f'{spec}, valero, unbranded, van nuys, shell oil, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SL6 T9 {spec}': f'{spec}, valero, unbranded, carson, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SO4 T12 {spec}': f'{spec}, marathon, unbranded, orange, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SO4 T2 {spec}': f'{spec}, marathon, unbranded, long beach, bp oil, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SO4 T22 {spec}': f'{spec}, marathon, unbranded, wilmington, tesoro, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SO4 T3 {spec}': f'{spec}, marathon, unbranded, south gate, bp oil, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SR5 T18 {spec}': f'{spec}, shell, branded, signal hill, shell oil, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SR5 T19 {spec}': f'{spec}, shell, branded, van nuys, shell oil, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SR5 T9 {spec}': f'{spec}, shell, branded, carson, kinder morgan, los angeles', 
            f'RACKM0{net_gross_letter} PO6 SSG T15 {spec}': f'{spec}, toledo refining, , vernon, exxonmobil, los angeles', 
        }, inplace=True)
        fresno_df.rename(columns={
            f'RACKK0{net_gross_letter} PO6 S43 T1 {spec}': f'{spec}, bp products, unbranded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 S7H T1 {spec}': f'{spec}, flyers energy, , , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 S7I T1 {spec}': f'{spec}, tesoro exxon, , , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SA3 T1 {spec}': f'{spec}, chevron, branded, kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SIA T1 {spec}': f'{spec}, conocophillips, branded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SJA T1 {spec}': f'{spec}, conocophillips, unbranded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SK8 T1 {spec}': f'{spec}, valero, branded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SL6 T1 {spec}': f'{spec}, valero, unbranded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SO4 T1 {spec}': f'{spec}, marathon, unbranded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SP4 T1 {spec}': f'{spec}, marathon, branded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SQF T1 {spec}': f'{spec}, idemitsu apollo, , , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SR5 T1 {spec}': f'{spec}, shell, branded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SS5 T1 {spec}': f'{spec}, shell, unbranded, , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SSG T1 {spec}': f'{spec}, toledo refining, , , kinder morgan, fresno', 
            f'RACKK0{net_gross_letter} PO6 SX3 T1 {spec}': f'{spec}, exxon, branded, , kinder morgan, fresno', 
        }, inplace=True)
        barstow_df.rename(columns={
            f'RACKF0{net_gross_letter} PO6 SL6 T1 {spec}': f'{spec}, valero, unbranded, , kinder morgan, barstow', 
            f'RACKF0{net_gross_letter} PO6 SA3 T1 {spec}': f'{spec}, chevron, branded, , kinder morgan, barstow', 
            f'RACKF0{net_gross_letter} PO6 SK8 T1 {spec}': f'{spec}, valero, branded, , kinder morgan, barstow', 
            f'RACKF0{net_gross_letter} PO6 SO4 T1 {spec}': f'{spec}, marathon, unbranded, , kinder morgan, barstow', 
        }, inplace=True)
        chico_df.rename(columns={
            f'RACKH0{net_gross_letter} PO6 S43 T1 {spec}': f'{spec}, bp products, unbranded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 S7H T1 {spec}': f'{spec}, flyers energy, , , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 S7I T1 {spec}': f'{spec}, tesoro exxon, , , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SA3 T1 {spec}': f'{spec}, chevron, branded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SIA T1 {spec}': f'{spec}, conocophillips, branded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SJA T1 {spec}': f'{spec}, conocophillips, unbranded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SK8 T1 {spec}': f'{spec}, valero, branded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SL6 T1 {spec}': f'{spec}, valero, unbranded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SO4 T1 {spec}': f'{spec}, marathon, unbranded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SP4 T1 {spec}': f'{spec}, marathon, branded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SQF T1 {spec}': f'{spec}, idemitsu apollo, , , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SR5 T1 {spec}': f'{spec}, shell, branded, , kinder morgan, chico', 
            f'RACKH0{net_gross_letter} PO6 SSG T1 {spec}': f'{spec}, toledo refining, kinder morgan, chico', 
        }, inplace=True)
        colton_df.rename(columns={
            f'RACKI0{net_gross_letter} PO6 S43 T4 {spec}': f'{spec}, bp products, unbranded, , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SA3 T4 {spec}': f'{spec}, chevron, branded, , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SIA T7 {spec}': f'{spec}, conocophillips, branded, , phillips 66, colton', 
            f'RACKI0{net_gross_letter} PO6 SK8 T4 {spec}': f'{spec}, valero, branded, , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SL6 T4 {spec}': f'{spec}, valero, unbranded, , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SMC T4 {spec}': f'{spec}, tesoro shell, branded, , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SO4 T4 {spec}': f'{spec}, marathon, unbranded, , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SQF T4 {spec}': f'{spec}, demitsu apollo, , , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SR5 T4 {spec}': f'{spec}, shell, branded, , kinder morgan, colton', 
            f'RACKI0{net_gross_letter} PO6 SSG T4 {spec}': f'{spec}, toledo refining, , , kinder morgan, colton', 
        }, inplace=True)
        imperial_df.rename(columns={
            f'RACKL0{net_gross_letter} PO6 SK8 T1 {spec}': f'{spec}, valero, branded, , kinder morgan, imperial', 
            f'RACKL0{net_gross_letter} PO6 SL6 T1 {spec}': f'{spec}, valero, unbranded, , kinder morgan, imperial', 
            f'RACKL0{net_gross_letter} PO6 SMC T1 {spec}': f'{spec}, tesoro shell, branded, , kinder morgan, imperial', 
            f'RACKL0{net_gross_letter} PO6 S04 T1 {spec}': f'{spec}, marathon, unbranded, , kinder morgan, imperial', 
            f'RACKL0{net_gross_letter} PO6 SQF T1 {spec}': f'{spec}, idemitsu apollo, , , kinder morgan, imperial', 
            f'RACKL0{net_gross_letter} PO6 SR5 T1 {spec}': f'{spec}, shell, branded, , kinder morgan, imperial', 
        }, inplace=True)
        sacramento_df.rename(columns={
            f'RACKN0{net_gross_letter} PO6 S43 T1 {spec}': f'{spec}, bp products, unbranded, west sacramento, buckeye, sacramento', 
            f'RACKN0{net_gross_letter} PO6 S43 T3 {spec}': f'{spec}, bp products, unbranded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 S7H T3 {spec}': f'{spec}, flyers energy, , rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 S7H T7 {spec}': f'{spec}, flyers energy, , , phillips 66, sacramento', 
            f'RACKN0{net_gross_letter} PO6 S7I T3 {spec}': f'{spec}, tesoro exxon, , rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SA3 T2 {spec}': f'{spec}, chevron, branded, , chevron, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SIA T3 {spec}': f'{spec}, conocophillips, branded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SIA T7 {spec}': f'{spec}, conocophillips, branded, phillips 66, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SJA T3 {spec}': f'{spec}, conocophillips, unbranded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SJA T7 {spec}': f'{spec}, conocophillips, unbranded, phillips 66, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SK8 T3 {spec}': f'{spec}, valero, branded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SL6 T3 {spec}': f'{spec}, alero, unbranded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SO4 T3 {spec}': f'{spec}, marathon, unbranded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SP4 T3 {spec}': f'{spec}, marathon, branded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SQF T3 {spec}': f'{spec}, idemitsu apollo, , rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SR5 T1 {spec}': f'{spec}, shell, branded, west sacramento, buckeye, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SR5 T3 {spec}': f'{spec}, shell, branded, rancho cordova, kinder morgan, sacramento', 
            f'RACKN0{net_gross_letter} PO6 SSG T3 {spec}': f'{spec}, toledo refining, , rancho cordova, kinder morgan, sacramento', 
        }, inplace=True)
        san_diego_df.rename(columns={
            f'RACKO0{net_gross_letter} PO6 S43 T3 {spec}': f'{spec}, bp products, unbranded, , kinder morgan, san diego', 
            f'RACKO0{net_gross_letter} PO6 SA3 T2 {spec}': f'{spec}, chevron, branded, , chevron, san diego', 
            f'RACKO0{net_gross_letter} PO6 SK8 T3 {spec}': f'{spec}, valero, branded, , kinder morgan, san diego', 
            f'RACKO0{net_gross_letter} PO6 SL6 T3 {spec}': f'{spec}, valero, unbranded, , kinder morgan, san diego', 
            f'RACKO0{net_gross_letter} PO6 SO4 T3 {spec}': f'{spec}, marathon, unbranded, , kinder morgan, san diego', 
            f'RACKO0{net_gross_letter} PO6 SQF T3 {spec}': f'{spec}, idemitsu apollo, , , kinder morgan, san diego', 
            f'RACKO0{net_gross_letter} PO6 SR5 T3 {spec}': f'{spec}, shell, branded, , kinder morgan, san diego', 
            f'RACKO0{net_gross_letter} PO6 SSG T3 {spec}': f'{spec}, toledo refining, , , kinder morgan, san diego', 
        }, inplace=True)
        san_francisco_df.rename(columns={
            f'RACKP0{net_gross_letter} PO6 S26 T2 {spec}': f'{spec}, texaco, branded, avon, chevron, san francisco', 
            f'RACKP0{net_gross_letter} PO6 S43 T1 {spec}': f'{spec}, bp products, unbranded, richmond, bp oil products, san francisco', 
            f'RACKP0{net_gross_letter} PO6 S7I T9 {spec}': f'{spec}, tesoro exxon, , martinez, tesoro, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SA3 T2 {spec}': f'{spec}, chevron, branded, avon, chevron, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SA3 T3 {spec}': f'{spec}, chevron, branded, richmond, chevron, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SIA T10 {spec}': f'{spec}, conocophillips, branded, richmond, phillips 66, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SJA T10 {spec}': f'{spec}, conocophillips, unbranded, richmond, phillips 66, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SK8 T3 {spec}': f'{spec}, valero, branded, richmond, chevron, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SK8 T4 {spec}': f'{spec}, valero, branded, benicia, valero refining, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SL6 T3 {spec}': f'{spec}, valero, unbranded, richmond, chevron, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SL6 T4 {spec}': f'{spec}, valero, unbranded, benicia, valero refining, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SO4 T9 {spec}': f'{spec}, marathon, unbranded, martinez, tesoro, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SP4 T9 {spec}': f'{spec}, marathon, branded, martinez, tesoro, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SR5 T6 {spec}': f'{spec}, shell, branded, , martinez, shell oil products, san francisco', 
            f'RACKP0{net_gross_letter} PO6 SSG T6 {spec}': f'{spec}, toledo refining, , martinez, shell oil products, san francisco', 
        }, inplace=True)
        san_jose_df.rename(columns={
            f'RACKQ0{net_gross_letter} PO6 S43 T3 {spec}': f'{spec}, bp products, unbranded, , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 S7H T3 {spec}': f'{spec}, flyers energy, , , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 S7I T3 {spec}': f'{spec}, tesoro exxon, , , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SA3 T1 {spec}': f'{spec}, chevron, branded, , chevron, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SIA T3 {spec}': f'{spec}, conocophillips, branded, , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SJA T3 {spec}': f'{spec}, conocophillips, unbranded, , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SK8 T3 {spec}': f'{spec}, valero, branded, , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SL6 T3 {spec}': f'{spec}, valero, unbranded, , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SO4 T3 {spec}': f'{spec}, marathon, unbranded, , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SO4 T4 {spec}': f'{spec}, marathon, unbranded, , shell oil products, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SP4 T3 {spec}': f'{spec}, marathon, branded, , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SP4 T4 {spec}': f'{spec}, marathon, branded, , shell oil products, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SQF T3 {spec}': f'{spec}, idemitsu apollo, , , kinder morgan, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SR5 T4 {spec}': f'{spec}, shell, branded, , shell oil products, san jose', 
            f'RACKQ0{net_gross_letter} PO6 SSG T3 {spec}': f'{spec}, toledo refining, , , kinder morgan, san jose', 
        }, inplace=True)
        stockton_df.rename(columns={
            f'RACKR0{net_gross_letter} PO6 S26 T2 {spec}': f'{spec}, texaco, branded, banta, chevron, stockton', 
            f'RACKR0{net_gross_letter} PO6 S43 T1 {spec}': f'{spec}, bp products, unbranded, , buckeye, stockton', 
            f'RACKR0{net_gross_letter} PO6 S43 T5 {spec}': f'{spec}, bp products, unbranded, , nustar, stockton', 
            f'RACKR0{net_gross_letter} PO6 S7H T5 {spec}': f'{spec}, flyers energy, , , nustar, stockton', 
            f'RACKR0{net_gross_letter} PO6 S7I T6 {spec}': f'{spec}, tesoro exxon, , , tesoro, stockton', 
            f'RACKR0{net_gross_letter} PO6 SA3 T2 {spec}': f'{spec}, chevron, branded, banta, chevron, stockton', 
            f'RACKR0{net_gross_letter} PO6 SIA T5 {spec}': f'{spec}, conocophillips, branded, , nustar, stockton', 
            f'RACKR0{net_gross_letter} PO6 SJA T5 {spec}': f'{spec}, conocophillips, unbranded, , nustar, stockton', 
            f'RACKR0{net_gross_letter} PO6 SK8 T5 {spec}': f'{spec}, valero, branded, , nustar, stockton', 
            f'RACKR0{net_gross_letter} PO6 SL6 T5 {spec}': f'{spec}, valero, unbranded, , nustar, stockton', 
            f'RACKR0{net_gross_letter} PO6 SO4 T6 {spec}': f'{spec}, marathon, unbranded, , tesoro, stockton', 
            f'RACKR0{net_gross_letter} PO6 SP4 T6 {spec}': f'{spec}, marathon, branded, , tesoro, stockton', 
            f'RACKR0{net_gross_letter} PO6 SQF T5 {spec}': f'{spec}, idemitsu apollo, , , nustar, stockton', 
            f'RACKR0{net_gross_letter} PO6 SR5 T4 {spec}': f'{spec}, shell, branded, , shell oil products, stockton', 
            f'RACKR0{net_gross_letter} PO6 SSG T5 {spec}': f'{spec}, toledo refining,  , , nustar, stockton', 
        }, inplace=True)

    los_angeles_df = reshape_wide_to_long(los_angeles_df)
    fresno_df = reshape_wide_to_long(fresno_df)
    barstow_df = reshape_wide_to_long(barstow_df)
    chico_df = reshape_wide_to_long(chico_df)   
    colton_df = reshape_wide_to_long(colton_df) 
    imperial_df = reshape_wide_to_long(imperial_df) 
    sacramento_df = reshape_wide_to_long(sacramento_df) 
    san_diego_df = reshape_wide_to_long(san_diego_df)   
    san_francisco_df = reshape_wide_to_long(san_francisco_df)
    san_jose_df = reshape_wide_to_long(san_jose_df)
    stockton_df = reshape_wide_to_long(stockton_df)
    bakersfield_df = reshape_wide_to_long(bakersfield_df)

    dfs = [los_angeles_df, fresno_df, barstow_df, chico_df, colton_df, imperial_df, 
       sacramento_df, san_diego_df, san_francisco_df, san_jose_df, stockton_df, 
       bakersfield_df]

    detailed_rack_df = pd.concat(dfs, ignore_index=True)

    # now let's rename some blank columns to make it clear that they're overall indices: 
    def assign_index_names(row):
        if row['company'] == '' and row['location of refiner'] == '' and row['distributor'] == '':
            if row['branded_indicator'] == '':
                return 'average'
            elif row['branded_indicator'] == 'unbranded':
                return 'unbranded average'
            elif row['branded_indicator'] == 'branded':
                return 'branded average'
        return row['company']  # Return the original company value if no conditions are met

    #detailed_rack_df.loc[detailed_rack_df['company'].isin(['branded average', 'unbranded average']), 'branded_indicator'] = ''

    # Apply the function to each row in the DataFrame
    detailed_rack_df['company'] = detailed_rack_df.apply(assign_index_names, axis=1)

    if net_gross == 'gross':
        detailed_rack_gross_df = detailed_rack_df
    if net_gross == 'net':
        detailed_rack_net_df = detailed_rack_df
    
detailed_rack_merged_df = pd.merge(detailed_rack_gross_df, detailed_rack_net_df, on=['date', 'city', 'company',
                                                            'distributor', 'location of refiner', 'branded_indicator'], how='outer')

# post-merge diagnostics, compare row counts
print(f'Rows in df1: {len(detailed_rack_gross_df)}')
print(f'Rows in df2: {len(detailed_rack_gross_df)}')
print(f'Rows in merged_df: {len(detailed_rack_merged_df)}')

# now merge with cpi data and create real prices for everything
cpi_df = pd.read_csv(f'{data}/cpi.csv')
cpi_df['date'] = pd.to_datetime(cpi_df['date'])

detailed_rack_merged_df = pd.merge(detailed_rack_merged_df, cpi_df, on='date', how='left')
detailed_rack_merged_df['all-urban cpi'] = detailed_rack_merged_df['all-urban cpi'].fillna(method='ffill')

cpi_anchor = pd.to_datetime('2023-03-01')
fixed_cpi = detailed_rack_merged_df.loc[detailed_rack_merged_df['date'] == cpi_anchor, 'all-urban cpi'].values[0]
detailed_rack_merged_df['price deflator'] = detailed_rack_merged_df['all-urban cpi'] / fixed_cpi

for net_gross in ['gross', 'net']:
    for spec in [f'dtn {net_gross} spread', f'dtn {net_gross} price']:
        detailed_rack_merged_df[f'{spec} (real)'] = (detailed_rack_merged_df[f'{spec} (nominal)']
                                          /detailed_rack_merged_df['price deflator'])

detailed_rack_merged_df['date'] = pd.to_datetime(detailed_rack_merged_df['date'])
start_date = pd.to_datetime('2012-05-01')
detailed_rack_merged_df = detailed_rack_merged_df.loc[detailed_rack_merged_df['date'] >= start_date]
current_date = datetime.now()
detailed_rack_merged_df = detailed_rack_merged_df.loc[detailed_rack_merged_df['date'] <= current_date]

detailed_rack_merged_df.to_csv(f'{data}/detailed_rack_prices.csv', index=False)