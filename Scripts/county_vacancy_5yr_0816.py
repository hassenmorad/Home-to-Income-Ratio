# County Housing Vacancy Rates
# Source: Census (census.data.gov) advanced search (Topics: 'Housing-Vacancy-Vacancy Rates'; Geography: All US Counties; Years: 2010-2018 ACS 5-Yr. Estimates)
import pandas as pd
import numpy as np
import os

master_df = pd.DataFrame()
counter = 0
for file in os.listdir('County Vacancy Per 5yr')[::3]:
    year = int(file[7:11])
    print(year)
    data_df = pd.read_csv('County Vacancy Per 5yr/' + file, skiprows=1, usecols=[0,1,2,14,18])
    data_df.columns = ['FIPS', 'County', 'Total_Units', 'Homeowner_Vacancy', 'Rental_Vacancy']
    
    drop = []
    for i,row in data_df.iterrows():
        if 'N' in row.values or '-' in row.values or '100-' in row.values or '(X)' in row.values:
            drop.append(i)
    print('counties excluded:', len(drop))        
    data_df = data_df.drop(drop)
    
    data_df.FIPS = data_df.FIPS.apply(lambda x:x[-5:]).astype(int)
    data_df = data_df[data_df.FIPS < 57000].sort_values('FIPS')
    data_df['Year'] = list(np.full(len(data_df), year-2))
        
    #dataframe.to_csv('county_vacancy_5yr_0816_' + str(year) + '.csv', index=False)
    master_df = pd.concat([master_df, data_df])
    counter += 1
    
master_df.to_csv('county_vacancy_5yr_0816.csv', index=False)