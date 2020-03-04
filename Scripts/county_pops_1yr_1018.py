# Percentage of homeowners & renters devoting 30+% of household income to housing
# Source: Census (census.data.gov) advanced search (Topics: 'Housing' & 'Income and Poverty'; Geography: All US Counties; Years: ACS 1-Yr. Estimates)
import pandas as pd
import numpy as np
import os

master_df = pd.DataFrame()
for file in os.listdir('County Population 1-yr')[::3]:
    year = int(file[7:11])
    print(year)
    df = pd.read_csv('County Population 1-yr/' + file)
    df = df[['GEO_ID', 'NAME', 'S0101_C01_001E']][1:]
    df.columns = ['FIPS', 'County', 'Population']
    df.Population = df.Population.astype(int)
    df.FIPS = df.FIPS.apply(lambda x:x[-5:]).astype(int)
    df['Year'] = list(np.full(len(df), year))
    df = df.sort_values(['Year', 'FIPS'])
    master_df = pd.concat([master_df, df])
    
master_df.to_csv('county_pops_1yr_1018.csv', index=False)