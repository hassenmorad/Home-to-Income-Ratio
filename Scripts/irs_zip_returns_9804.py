# Estimating zip code household count by number of IRS tax returns filed
import pandas as pd
import numpy as np
import os

zips9804 = os.listdir('IRS Zip')[-4:]  # Individual states need to be combined

master_df = pd.DataFrame()
years = [1998, 2001, 2002, 2004]
skprw = [6,6,6,12]
skpftr = [6,6,0,0]
id_loc = [6,6,6,8]
counter = 0

for folder in zips9804:
    print(years[counter])
    year_df = pd.DataFrame()
    for file in os.listdir('IRS Zip/' + folder)[:51]:
        state_df = pd.read_excel('IRS Zip/' + folder + '/' + file, usecols=[0,1], skiprows=skprw[counter], skipfooter=skpftr[counter])
        state_df.columns = ['Zip', 'Returns']
        state_df.Zip = state_df.Zip.astype(str).apply(lambda x:x.strip())
        under_id = state_df[state_df.Zip.str.contains('Under')].index[1]  # Second entry is the real starting point
        
        ids = list(range(under_id-1,len(state_df), id_loc[counter]))
        state_df = state_df.iloc[ids].drop_duplicates(subset=['Zip'])
        state_df['State'] = np.full(len(state_df), file[-6:-4].upper())
        year_df = pd.concat([year_df, state_df])
    year_df['Year'] = np.full(len(year_df), years[counter])
    master_df = pd.concat([master_df, year_df.replace('',np.nan).dropna()])
    counter += 1

master_df.Zip = master_df.Zip.astype(int)
master_df.Returns = master_df.Returns.astype(int)
master_df = master_df[(master_df.Zip > 0) & (master_df.Zip < 99999)].sort_values(['Zip', 'Year'])
master_df[['Year', 'State', 'Zip', 'Returns']].to_csv('irs_zip_returns_9804.csv', index=False)