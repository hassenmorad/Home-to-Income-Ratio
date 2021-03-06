# Percentage of homeowners & renters devoting 30+% of household income to housing
# Source: Census (census.data.gov) advanced search (Topics: 'Housing' & 'Income and Poverty'; Geography: All US Counties; Years: ACS 1-Yr. Estimates)
import pandas as pd
import numpy as np
import os

master_df = pd.DataFrame()
metadata = os.listdir('Counties 5yr')[1::3]
counter = 0
for file in os.listdir('Counties 5yr')[::3]:
    year = int(file[7:11])
    print(year, file)
    data_df = pd.read_csv('Counties 5yr/' + file)[1:]
    meta = pd.read_csv('Counties 5yr/' + metadata[counter])[1:]
    
    # Filtering onditions
    owner_cond = ((meta.id.str.contains('Owner-occupied housing')) | (meta.id.str.contains('owner-occupied housing')))
    renter_cond = ((meta.id.str.contains('Renter-occupied housing')) | (meta.id.str.contains('renter-occupied housing')))
    percentage_cond = (meta.id.str.contains('PERCENTAGE'))
    margin_cond = (~meta.id.str.contains('Margin'))
    median_cond = (meta.id.str.contains('Median'))

    home_cols = meta.GEO_ID[owner_cond & percentage_cond & margin_cond & (meta.id.str.contains('30'))][-5:].reset_index(drop=True)
    rent_cols = meta.GEO_ID[renter_cond & percentage_cond & margin_cond & (meta.id.str.contains('30'))][-5:].reset_index(drop=True)
    med_inc_cols = meta.GEO_ID[(owner_cond | renter_cond) & margin_cond & median_cond & (meta.id.str.contains('HOUSEHOLD INCOME'))].reset_index(drop=True)
    med_housing_cols = meta.GEO_ID[(owner_cond | renter_cond) & margin_cond & median_cond & (meta.id.str.contains('HOUSING COSTS'))].reset_index(drop=True)
    homeowner_units_col = meta.GEO_ID[meta.id.str.contains('Owner-occupied housing')].reset_index(drop=True).iloc[0]
    renter_units_col = meta.GEO_ID[meta.id.str.contains('Renter-occupied housing')].reset_index(drop=True).iloc[0]

    # Excluding double-counts (due to median appearing in Percentage and Raw Dollar cols for 2017 & 2018)
    if year > 2016:
        med_inc_cols = med_inc_cols[::2]
        med_housing_cols = med_housing_cols[::2]
    
    cols = list(home_cols.values) + list(rent_cols.values) + list(med_inc_cols) + list(med_housing_cols) + [homeowner_units_col] + [renter_units_col]
    data_df = data_df.loc[:,['GEO_ID', 'NAME'] + cols].sort_values('GEO_ID')
    
    drop = []
    for i,row in data_df.iterrows():
        if 'N' in row.values or '-' in row.values or '100-' in row.values or '(X)' in row.values:
            drop.append(i)
    print('counties excluded:', len(drop))        
    data_df = data_df.drop(drop)
    for col in data_df.columns[2:]:
        data_df[col] = data_df[col].astype(float)
    
    data_df = data_df.rename({'GEO_ID':'FIPS', 'NAME':'County'}, axis=1)
    data_df.FIPS = data_df.FIPS.apply(lambda x:x[-5:]).astype(int)
    data_df = data_df[data_df.FIPS < 57000].sort_values('FIPS')
    
    owners = []
    renters = []
    med_mort_inc = []
    med_rent_inc = []
    med_mort = []
    med_rent = []
    owned_units = []
    rented_units = []
    for fips in data_df.FIPS.unique():
        df = data_df[data_df.FIPS == fips]
        owners.append(round(df.values[0][2:7].sum(),1))
        renters.append(round(df.values[0][7:12].sum(),1))
        med_mort_inc.append(round(df.values[0][12] / 12,0))
        med_rent_inc.append(round(df.values[0][13] / 12,0))
        med_mort.append(df.values[0][14])
        med_rent.append(df.values[0][15])
        owned_units.append(df.values[0][16])
        rented_units.append(df.values[0][17])
    
    dataframe = pd.DataFrame({'Year':list(np.full(len(owners), year)), 'FIPS':data_df.FIPS.unique(), 'County':data_df.County.unique(), 'Owners30':owners, 
                              'Renters30':renters, 'Med_Mort':med_mort, 'Med_Rent':med_rent, 'Med_Mort_Inc':med_mort_inc, 'Med_Rent_Inc':med_rent_inc, 
                              'Owned_Units':owned_units, 'Rented_Units':rented_units})
    dataframe['Mort_Less30'] = 100 - dataframe.Owners30
    dataframe['Rent_Less30'] = 100 - dataframe.Renters30
    dataframe['Total_Units'] = dataframe.Owned_Units + dataframe.Rented_Units
    dataframe['Rent_Units_Per1'] = round(dataframe.Rented_Units / dataframe.Total_Units, 3)
    dataframe['Rent_Units_Per2'] = dataframe.Rent_Units_Per1 * 100
    dataframe['Mort_Per_Inc1'] = round(dataframe.Med_Mort / dataframe.Med_Mort_Inc, 3)
    dataframe['Mort_Per_Inc2'] = dataframe.Mort_Per_Inc1 * 100
    dataframe['Rent_Per_Inc1'] = round(dataframe.Med_Rent / dataframe.Med_Rent_Inc, 3)
    dataframe['Rent_Per_Inc2'] = dataframe.Rent_Per_Inc1 * 100    
    
    dataframe = dataframe[~((dataframe.Rent_Per_Inc1 > .5) & (dataframe.Total_Units < 10000))]  # Excluding outliers (a few low pop counties from each year)
    dataframe.to_csv('county_rent_vs_mort_and_inc_5yr_' + str(year) + '.csv', index=False)
    
    master_df = pd.concat([master_df, dataframe])
    
    counter += 1
    
master_df.to_csv('county_rent_vs_mort_and_inc_5yr.csv', index=False)