import pandas as pd
from pathlib import Path
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

# bakersfield detailed rack price data 
def extract_data(city):
    df = pd.read_excel(f'{raw_data}/bloomberg_detailed_rack.xlsx', sheet_name=f'{city}_import')
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
                     ['RACKM0G', 'RACKK0G', 'RACKF0G', 'RACKH0G', 'RACKI0G', 'RACKL0G',
                      'RACKN0G', 'RACKO0G', 'RACKP0G', 'RACKQ0G', 'RACKR0G',
                      'RACKE0G']):
    df['date'] = pd.to_datetime(df['date'])
    df.rename(columns={f'{code} PO6 R Index': f'{city} rack price'}, inplace=True)
    cols_exclude = ['date', f'{city} rack price']
    vars_interest = [col for col in df.columns if col not in cols_exclude]
    for var in vars_interest:
        df[f'{var} spread (nominal)'] = (df[f'{var}'] - df[f'{city} rack price'])
    for spec in ['Index spread (nominal)', 'Index']:
        df.rename(columns = {f'{code} PO6 U {spec}': f'{city} unbranded rack {spec}',
                         f'{code} PO6 B {spec}': f'{city} branded rack {spec}'}, inplace=True)
# now unfortunately we have to rename manually the rest of the columns
for spec in ['Index spread (nominal)', 'Index']:
    bakersfield_df.rename(columns = {
        f'RACKE0G PO6 S26 T1 {spec}': f'texaco branded, bakersfield, kern, bakersfield rack {spec}', 
        f'RACKE0G PO6 SA3 T1 {spec}': f'chevron branded, bakersfield, kern, bakersfield rack {spec}', 
        f'RACKE0G PO6 SR5 T1 {spec}': f'shell branded, bakersfield, kern, bakersfield rack {spec}', 
        f'RACKE0G PO6 SX3 T1 {spec}': f'exxon branded, bakersfield, kern, bakersfield rack {spec}'
        }, inplace=True)
    los_angeles_df.drop(columns=[f'RACKM0G PO6 SK8 T19 {spec}'], inplace=True)
    los_angeles_df.rename(columns={
        f'RACKM0G PO6 SSG T12 {spec}': f'toledo refining, orange, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 S43 T9 {spec}': f'bp products unbranded, carson, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SA3 T6 {spec}': f'chevron branded, huntington beach, chevron, los angeles rack {spec}', 
        f'RACKM0G PO6 SA3 T7 {spec}': f'chevron branded, montebello, chevron, los angeles rack {spec}', 
        f'RACKM0G PO6 SA3 T8 {spec}': f'chevron branded, van nuys, chevron, los angeles rack {spec}', 
        f'RACKM0G PO6 SIA T25 {spec}': f'conocophillips branded, los angeles, phillips 66, los angeles rack {spec}', 
        f'RACKM0G PO6 SK8 T12 {spec}': f'valero branded, orange, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SK8 T19 {spec}': f'valero branded, orange, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SK8 T9 {spec}': f'valero branded, carson, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SL6 T12 {spec}': f'valero unbranded, orange, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SL6 T18 {spec}': f'valero unbranded, signal hill, shell oil, los angeles rack {spec}', 
        f'RACKM0G PO6 SL6 T19 {spec}': f'valero unbranded, van nuys, shell oil, los angeles rack {spec}', 
        f'RACKM0G PO6 SL6 T9 {spec}': f'valero unbranded, carson, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SO4 T12 {spec}': f'marathon unbranded, orange, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SO4 T2 {spec}': f'marathon unbranded, long beach, bp oil, los angeles rack {spec}', 
        f'RACKM0G PO6 SO4 T22 {spec}': f'marathon unbranded, wilmington, tesoro, los angeles rack {spec}', 
        f'RACKM0G PO6 SO4 T3 {spec}': f'marathon unbranded, south gate, bp oil, los angeles rack {spec}', 
        f'RACKM0G PO6 SR5 T18 {spec}': f'shell branded, signal hill, shell oil, los angeles rack {spec}', 
        f'RACKM0G PO6 SR5 T19 {spec}': f'shell branded, van nuys, shell oil, los angeles rack {spec}', 
        f'RACKM0G PO6 SR5 T9 {spec}': f'shell branded, carson, kinder morgan, los angeles rack {spec}', 
        f'RACKM0G PO6 SSG T15 {spec}': f'toledo refining, vernon, exxonmobil, los angeles rack {spec}', 
    }, inplace=True)
    fresno_df.rename(columns={
        f'RACKK0G PO6 S43 T1 {spec}': f'bp products unbranded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 S7H T1 {spec}': f'flyers energy, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 S7I T1 {spec}': f'tesoro exxon, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SA3 T1 {spec}': f'chevron branded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SIA T1 {spec}': f'conocophillips branded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SJA T1 {spec}': f'conocophillips unbranded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SK8 T1 {spec}': f'valero branded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SL6 T1 {spec}': f'valero unbranded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SO4 T1 {spec}': f'marathon unbranded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SP4 T1 {spec}': f'marathon branded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SQF T1 {spec}': f'idemitsu apollo, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SR5 T1 {spec}': f'shell branded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SS5 T1 {spec}': f'shell unbranded, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SSG T1 {spec}': f'toledo refining, fresno, kinder morgan, fresno rack {spec}', 
        f'RACKK0G PO6 SX3 T1 {spec}': f'exxon branded, fresno, kinder morgan, fresno rack {spec}', 
    }, inplace=True)
    barstow_df.rename(columns={
        f'RACKF0G PO6 SL6 T1 {spec}': f'valero unbranded, dagget, kinder morgan, barstow rack {spec}', 
        f'RACKF0G PO6 SA3 T1 {spec}': f'chevron branded, daggett, kinder morgan, barstow rack {spec}', 
        f'RACKF0G PO6 SK8 T1 {spec}': f'valero branded, daggett, kinder morgan, barstow rack {spec}', 
        f'RACKF0G PO6 SO4 T1 {spec}': f'marathon unbranded, daggett, kinder morgan, barstow rack {spec}', 
    }, inplace=True)
    chico_df.rename(columns={
        f'RACKH0G PO6 S43 T1 {spec}': f'bp products unbranded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 S7H T1 {spec}': f'flyers energy, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 S7I T1 {spec}': f'tesoro exxon, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SA3 T1 {spec}': f'chevron branded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SIA T1 {spec}': f'conocophillips branded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SJA T1 {spec}': f'conocophillips unbranded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SK8 T1 {spec}': f'valero branded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SL6 T1 {spec}': f'valero unbranded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SO4 T1 {spec}': f'marathon unbranded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SP4 T1 {spec}': f'marathon branded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SQF T1 {spec}': f'idemitsu apollo, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SR5 T1 {spec}': f'shell branded, chico, kinder morgan, chico rack {spec}', 
        f'RACKH0G PO6 SSG T1 {spec}': f'toledo refining, chico, kinder morgan, chico rack {spec}', 
    }, inplace=True)
    colton_df.rename(columns={
        f'RACKI0G PO6 S43 T4 {spec}': f'bp products unbranded, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SA3 T4 {spec}': f'chevron branded, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SIA T7 {spec}': f'conocophillips branded, colton, phillips 66, colton rack {spec}', 
        f'RACKI0G PO6 SK8 T4 {spec}': f'valero branded, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SL6 T4 {spec}': f'valero unbranded, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SMC T4 {spec}': f'tesoro shell branded, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SO4 T4 {spec}': f'marathon unbranded, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SQF T4 {spec}': f'idemitsu apollo, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SR5 T4 {spec}': f'shell branded, colton, kinder morgan, colton rack {spec}', 
        f'RACKI0G PO6 SSG T4 {spec}': f'toledo refining, colton, kinder morgan, colton rack {spec}', 
    }, inplace=True)
    imperial_df.rename(columns={
        f'RACKL0G PO6 SK8 T1 {spec}': f'valero branded, imperial, kinder morgan, imperial rack {spec}', 
        f'RACKL0G PO6 SL6 T1 {spec}': f'valero unbranded, imperial, kinder morgan, imperial rack {spec}', 
        f'RACKL0G PO6 SMC T1 {spec}': f'tesoro shell branded, imperial, kinder morgan, imperial rack {spec}', 
        f'RACKL0G PO6 S04 T1 {spec}': f'marathon unbranded, imperial, kinder morgan, imperial rack {spec}', 
        f'RACKL0G PO6 SQF T1 {spec}': f'idemitsu apollo, imperial, kinder morgan, imperial rack {spec}', 
        f'RACKL0G PO6 SR5 T1 {spec}': f'shell branded, imperial, kinder morgan, imperial rack {spec}', 
    }, inplace=True)
    sacramento_df.rename(columns={
        f'RACKN0G PO6 S43 T1 {spec}': f'bp products unbranded, west sacramento, buckeye, sacramento rack {spec}', 
        f'RACKN0G PO6 S43 T3 {spec}': f'bp products unbranded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 S7H T3 {spec}': f'flyers energy, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 S7H T7 {spec}': f'flyers energy, sacramento, phillips 66, sacramento rack {spec}', 
        f'RACKN0G PO6 S7I T3 {spec}': f'tesoro exxon, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SA3 T2 {spec}': f'chevron branded, sacramento, chevron, sacramento rack {spec}', 
        f'RACKN0G PO6 SIA T3 {spec}': f'conocophillips branded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SIA T7 {spec}': f'conocophillips branded, sacramento, phillips 66, sacramento rack {spec}', 
        f'RACKN0G PO6 SJA T3 {spec}': f'conocophillips unbranded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SJA T7 {spec}': f'conocophillips unbranded, sacramento, phillips 66, sacramento rack {spec}', 
        f'RACKN0G PO6 SK8 T3 {spec}': f'valero branded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SL6 T3 {spec}': f'valero unbranded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SO4 T3 {spec}': f'marathon unbranded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SP4 T3 {spec}': f'marathon branded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SQF T3 {spec}': f'idemitsu apollo, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SR5 T1 {spec}': f'shell branded, west sacramento, buckeye, sacramento rack {spec}', 
        f'RACKN0G PO6 SR5 T3 {spec}': f'shell branded, rancho cordova, kinder morgan, sacramento rack {spec}', 
        f'RACKN0G PO6 SSG T3 {spec}': f'toledo refining, rancho cordova, kinder morgan, sacramento rack {spec}', 
    }, inplace=True)
    san_diego_df.rename(columns={
        f'RACKO0G PO6 S43 T3 {spec}': f'bp products unbranded, san diego, kinder morgan, san diego rack {spec}', 
        f'RACKO0G PO6 SA3 T2 {spec}': f'chevron branded, san diego, chevron, san diego rack {spec}', 
        f'RACKO0G PO6 SK8 T3 {spec}': f'valero branded, san diego, kinder morgan, san diego rack {spec}', 
        f'RACKO0G PO6 SL6 T3 {spec}': f'valero unbranded, san diego, kinder morgan, san diego rack {spec}', 
        f'RACKO0G PO6 SO4 T3 {spec}': f'marathon unbranded, san diego, kinder morgan, san diego rack {spec}', 
        f'RACKO0G PO6 SQF T3 {spec}': f'idemitsu apollo, san diego, kinder morgan, san diego rack {spec}', 
        f'RACKO0G PO6 SR5 T3 {spec}': f'shell branded, san diego, kinder morgan, san diego rack {spec}', 
        f'RACKO0G PO6 SSG T3 {spec}': f'toledo refining, san diego, kinder morgan, san diego rack {spec}', 
    }, inplace=True)
    san_francisco_df.rename(columns={
        f'RACKP0G PO6 S26 T2 {spec}': f'texaco branded, avon, chevron, san francisco rack {spec}', 
        f'RACKP0G PO6 S43 T1 {spec}': f'bp products unbranded, richmond, bp oil products, san francisco rack {spec}', 
        f'RACKP0G PO6 S7I T9 {spec}': f'tesoro exxon, martinez, tesoro, san francisco rack {spec}', 
        f'RACKP0G PO6 SA3 T2 {spec}': f'chevron branded, avon, chevron, san francisco rack {spec}', 
        f'RACKP0G PO6 SA3 T3 {spec}': f'chevron branded, richmond, chevron, san francisco rack {spec}', 
        f'RACKP0G PO6 SIA T10 {spec}': f'conocophillips branded, richmond, phillips 66, san francisco rack {spec}', 
        f'RACKP0G PO6 SJA T10 {spec}': f'conocophillips unbranded, richmond, phillips 66, san francisco rack {spec}', 
        f'RACKP0G PO6 SK8 T3 {spec}': f'valero branded, richmond, chevron, san francisco rack {spec}', 
        f'RACKP0G PO6 SK8 T4 {spec}': f'valero branded, benicia, valero refining, san francisco rack {spec}', 
        f'RACKP0G PO6 SL6 T3 {spec}': f'valero unbranded, richmond, chevron, san francisco rack {spec}', 
        f'RACKP0G PO6 SL6 T4 {spec}': f'valero unbranded, benicia, valero refining, san francisco rack {spec}', 
        f'RACKP0G PO6 SO4 T9 {spec}': f'marathon unbranded, martinez, tesoro, san francisco rack {spec}', 
        f'RACKP0G PO6 SP4 T9 {spec}': f'marathon branded, martinez, tesoro, san francisco rack {spec}', 
        f'RACKP0G PO6 SR5 T6 {spec}': f'shell branded, martinez, shell oil products, san francisco rack {spec}', 
        f'RACKP0G PO6 SSG T6 {spec}': f'toledo refining, martinez, shell oil products, san francisco rack {spec}', 
    }, inplace=True)

cpi_df = pd.read_csv(f'{data}/cpi.csv')
cpi_df['date'] = pd.to_datetime(cpi_df['date'])

detailed_rack_df = pd.merge(bakersfield_df, cpi_df, on='date', how='outer')
detailed_rack_df['all-urban cpi'] = detailed_rack_df['all-urban cpi'].fillna(method='ffill')
for df in [df for df in dfs if df is not bakersfield_df]:
    detailed_rack_df = pd.merge(detailed_rack_df, df, on='date', how='outer')

cpi_anchor = pd.to_datetime('2023-03-01')
fixed_cpi = detailed_rack_df.loc[detailed_rack_df['date'] == cpi_anchor, 'all-urban cpi'].values[0]
detailed_rack_df['price deflator'] = detailed_rack_df['all-urban cpi'] / fixed_cpi

detailed_rack_df['date'] = pd.to_datetime(detailed_rack_df['date'])
start_date = pd.to_datetime('2010-01-01')
detailed_rack_df = detailed_rack_df.loc[detailed_rack_df['date'] >= start_date]

detailed_rack_df.to_csv(f'{data}/detailed_rack_prices.csv', index=False)