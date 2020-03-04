# County Housing Vacancy Raw Numbers
# Source: Census (census.data.gov) advanced search (Topics: 'Housing-Vacancy-Vacancy Rates' ('Vacancy Status' table); Geography: All US Counties; Years: 2010-2018 ACS 1-Yr. Estimates)
import pandas as pd
import numpy as np
import os

master_df = pd.DataFrame()
counter = 0
for file in os.listdir('County Vacancy Raw 1yr')[::3]:
    year = int(file[7:11])
    print(year)
    data_df = pd.read_csv('County Vacancy Raw 1yr/' + file, skiprows=1, usecols=[0,1,2,4,6,8,10])
    data_df.columns = ['FIPS', 'County', 'Total_Vacant', 'For_Rent', 'Rental_Unoccupied', 'For_Sale', 'Sold_Unoccupied']
    
    drop = []
    for i,row in data_df.iterrows():
        if 'N' in row.values or '-' in row.values or '100-' in row.values or '(X)' in row.values:
            drop.append(i)
    print('counties excluded:', len(drop))        
    data_df = data_df.drop(drop)
    
    data_df.FIPS = data_df.FIPS.apply(lambda x:x[-5:]).astype(int)
    data_df = data_df[data_df.FIPS < 57000].sort_values('FIPS')
    data_df['Year'] = list(np.full(len(data_df), year))
        
    master_df = pd.concat([master_df, data_df])
    counter += 1

# Total unoccupied rent & sold units (to calculate % of vacant units and provide context for how many rent/sale units exist)
master_df['Rental_Vacant'] = master_df.For_Rent + master_df.Rental_Unoccupied
master_df['Sold_Vacant'] = master_df.For_Sale + master_df.Sold_Unoccupied
master_df = master_df.drop(['For_Rent', 'Rental_Unoccupied', 'For_Sale', 'Sold_Unoccupied'], axis=1)
master_df.to_csv('county_vacancy_raw_1yr_1018.csv', index=False)