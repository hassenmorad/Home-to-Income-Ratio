# Combining returns for each zip code (separated by household income) - 05-08 data
import pandas as pd
import numpy as np
import os

zips0508 = os.listdir('IRS Zip')[:4]
master_df = pd.DataFrame()
years = list(range(2005, 2009))
cols = [[0,1,3], [0,2,3], [0,1,3], [0,1,3]]
counter = 0

for file in zips0508:
    print(years[counter])
    df = pd.read_csv('IRS Zip/' + file, usecols=cols[counter]).dropna()
    df.columns = ['State', 'Zip', 'Returns']
    returns = []
    states = []
    for zipcode in df.Zip.unique():
        zip_df = df[df.Zip == zipcode]
        returns.append(zip_df.Returns.sum())
        states.append(zip_df.State.iloc[0])
    yr_df = pd.DataFrame({'Year':np.full(len(returns), years[counter]), 'State':states, 'Zip':df.Zip.unique(), 'Returns':returns})
    master_df = pd.concat([master_df, yr_df])
    counter += 1
    
master_df.State = master_df.State.apply(lambda x:x.upper())
master_df.Zip = master_df.Zip.astype(int)
master_df.Returns = master_df.Returns.astype(int)
master_df = master_df[(master_df.Zip > 0) & (master_df.Zip < 99999)].sort_values(['Zip', 'Year'])
master_df.to_csv('irs_zip_returns_0508.csv', index=False)