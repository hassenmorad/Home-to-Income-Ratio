# Percentage of homeowners & renters devoting 30+% of household income to housing
# Source: Census (census.data.gov) advanced search (Topics: 'Housing' & 'Income and Poverty'; Geography: All US Counties; Years: ACS 1-Yr. Estimates)
import pandas as pd
import numpy as np
import os

master_df = pd.DataFrame()
metadata = os.listdir('US 1yr')[1::3]
counter = 0
for file in os.listdir('US 1yr')[::3]:
    year = int(file[7:11])
    print(year, file)
    data_df = pd.read_csv('US 1yr/' + file)[1:]
    meta = pd.read_csv('US 1yr/' + metadata[counter])[1:]
    
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
    data_df = data_df.loc[:,['NAME'] + cols]
           
    for col in data_df.columns[1:]:
        data_df[col] = data_df[col].astype(float)
    
    data_df = data_df.rename({'NAME':'Region'}, axis=1)
    
    owners = []
    renters = []
    med_mort_inc = []
    med_rent_inc = []
    med_mort = []
    med_rent = []
    owned_units = []
    rented_units = []
    for region in data_df.Region.unique():
        df = data_df[data_df.Region == region]
        owners.append(round(df.values[0][1:6].sum(),1))
        renters.append(round(df.values[0][6:11].sum(),1))
        med_mort_inc.append(round(df.values[0][11] / 12,0))
        med_rent_inc.append(round(df.values[0][12] / 12,0))
        med_mort.append(df.values[0][13])
        med_rent.append(df.values[0][14])
        owned_units.append(df.values[0][15])
        rented_units.append(df.values[0][16])
    
    dataframe = pd.DataFrame({'Year':list(np.full(len(owners), year)), 'Region':data_df.Region.unique(), 'Owners30':owners, 'Renters30':renters, 
                              'Med_Mort':med_mort, 'Med_Rent':med_rent, 'Med_Mort_Inc':med_mort_inc, 'Med_Rent_Inc':med_rent_inc, 
                              'Owned_Units':owned_units, 'Rented_Units':rented_units})
    dataframe['Mort_Rent_Diff'] = dataframe.Med_Rent - dataframe.Med_Mort
    dataframe['Rent_Mort_Diff'] = dataframe.Med_Mort - dataframe.Med_Rent
    dataframe['Rent_Mort_Diff_div_Rent'] = round(dataframe.Rent_Mort_Diff / dataframe.Med_Rent * 100, 2)
    dataframe['MR_Diff_Per_Rent_Inc'] = round(dataframe.Mort_Rent_Diff / dataframe.Med_Rent_Inc * 100, 2)
    dataframe['RM_Diff_Per_Mort_Inc'] = round(dataframe.Rent_Mort_Diff / dataframe.Med_Mort_Inc * 100, 2)
    dataframe['Mort_Less30'] = 100 - dataframe.Owners30
    dataframe['Rent_Less30'] = 100 - dataframe.Renters30
    dataframe['Total_Units'] = dataframe.Owned_Units + dataframe.Rented_Units
    dataframe['Owned_Units_Per_dec'] = round(dataframe.Owned_Units / dataframe.Total_Units, 3)
    dataframe['Owned_Units_Per_whole'] = dataframe.Owned_Units_Per_dec * 100
    dataframe['Rent_Units_Per_dec'] = round(dataframe.Rented_Units / dataframe.Total_Units, 3)
    dataframe['Rent_Units_Per_whole'] = dataframe.Rent_Units_Per_dec * 100
    dataframe['Mort_Share_Inc_dec'] = round(dataframe.Med_Mort / dataframe.Med_Mort_Inc, 3)
    dataframe['Mort_Share_Inc_whole'] = dataframe.Mort_Share_Inc_dec * 100
    dataframe['Rent_Share_Inc_dec'] = round(dataframe.Med_Rent / dataframe.Med_Rent_Inc, 3)
    dataframe['Rent_Share_Inc_whole'] = dataframe.Rent_Share_Inc_dec * 100    
    
    dataframe.to_csv('national_rent_vs_mort_and_inc_1yr_' + str(year) + '.csv', index=False)
    
    master_df = pd.concat([master_df, dataframe])
    counter += 1
    
master_df.to_csv('national_rent_vs_mort_and_inc_1yr.csv', index=False)