# Combining returns for all zip codes (98-17)
import pandas as pd
import numpy as np
import os

zips0917 = os.listdir('IRS Zip')[4:-4]
master_df = pd.DataFrame()
years = list(range(2009, 2018))
counter = 0

for file in zips0917:
    print(years[counter])
    df = pd.read_csv('IRS Zip/' + file, usecols=[1,2,4]).dropna()
    df.columns = ['State', 'Zip', 'Returns']
    df['Year'] = list(np.full(len(df), years[counter]))
    master_df = pd.concat([master_df, df])
    counter += 1
    
# Filling in missing years
master_df.Returns = master_df.Returns.astype(int)
master_df.Zip = master_df.Zip.astype(int)
master_df = master_df[(master_df.Zip > 0) & (master_df.Zip < 99999)].sort_values(['Zip', 'Year'])
master_df[['Year', 'State', 'Zip', 'Returns']].to_csv('irs_zip_returns_0917.csv', index=False)