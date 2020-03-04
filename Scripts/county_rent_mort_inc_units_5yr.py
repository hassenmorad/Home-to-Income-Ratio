# Percentage of homeowners & renters devoting 30+% of household income to housing
# Source: Census (census.data.gov) advanced search (Topics: 'Housing' & 'Income and Poverty'; Geography: All US Counties; Years: ACS 5-Yr. Estimates)
import pandas as pd
import numpy as np
import os

county_area_df = pd.read_csv('counties_2010_pop_and_house_density.csv')  # Extracting county area (to calculate pop & housing density)
county_vacancy_df = pd.read_csv('county_vacancy_raw_5yr_0816.csv')  # Total units vacant
county_hh_df = pd.read_csv('irs_mig_91to2018.csv')  # Extracting county household count
county_pop_df = pd.read_csv('county_pops_5yr_0816.csv')  # Extracting county population count

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
    estimate_cond = (meta.id.str.contains('Estimate'))
    median_cond = (meta.id.str.contains('Median'))

    home_cols = meta.GEO_ID[owner_cond & percentage_cond & estimate_cond & (meta.id.str.contains('30'))][-5:].reset_index(drop=True)
    rent_cols = meta.GEO_ID[renter_cond & percentage_cond & estimate_cond & (meta.id.str.contains('30'))][-5:].reset_index(drop=True)
    med_inc_cols = meta.GEO_ID[(owner_cond | renter_cond) & estimate_cond & median_cond & (meta.id.str.contains('HOUSEHOLD INCOME'))].reset_index(drop=True)
    med_housing_cols = meta.GEO_ID[(owner_cond | renter_cond) & estimate_cond & median_cond & (meta.id.str.contains('HOUSING COSTS'))].reset_index(drop=True)
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
    
    dataframe = pd.DataFrame({'Year':list(np.full(len(owners), year-2)), 'FIPS':data_df.FIPS.unique(), 'County':data_df.County.unique(),
                              'Owners30':owners, 'Renters30':renters, 'Med_Mort':med_mort, 'Med_Rent':med_rent, 'Med_Mort_Inc':med_mort_inc,
                              'Med_Rent_Inc':med_rent_inc, 'Owner_Occupied_Units':owned_units, 'Renter_Occupied_Units':rented_units})
    
    dataframe['Occupied_Units'] = dataframe.Owner_Occupied_Units + dataframe.Renter_Occupied_Units
    dataframe['Mort_Rent_Diff'] = dataframe.Med_Rent - dataframe.Med_Mort
    dataframe['Rent_Mort_Diff'] = dataframe.Med_Mort - dataframe.Med_Rent
    dataframe['Rent_Mort_Diff_div_Rent'] = dataframe.Rent_Mort_Diff / dataframe.Med_Rent * 100
    dataframe['MR_Diff_Per_Rent_Inc'] = dataframe.Mort_Rent_Diff / dataframe.Med_Rent_Inc * 100
    dataframe['RM_Diff_Per_Mort_Inc'] = dataframe.Rent_Mort_Diff / dataframe.Med_Mort_Inc * 100
    dataframe['Mort_Less30'] = 100 - dataframe.Owners30  # Mortgage accounts for less than 30% of income  
    dataframe['Rent_Less30'] = 100 - dataframe.Renters30  # Rent accounts for less than 30% of income
    dataframe['Mort_Share_Inc'] = round(dataframe.Med_Mort / dataframe.Med_Mort_Inc, 3) * 100
    dataframe['Rent_Share_Inc'] = round(dataframe.Med_Rent / dataframe.Med_Rent_Inc, 3) * 100
        
    # Adding Household Count Column
    hh_df = county_hh_df[county_hh_df.Year == year-2]  # Year-2 since year represents the last year of the 5-yr period
    hh_dict = {}
    for fips in hh_df.FIPS.unique():
        fips_df = hh_df[hh_df.FIPS == fips]
        hh_dict[fips] = fips_df.Households.iloc[0]
    dataframe['Households'] = dataframe.FIPS.map(hh_dict)
    
    # Adding Population Count Column
    pop_df = county_pop_df[county_pop_df.Year == year-2]
    pop_dict = {}
    for fips in pop_df.FIPS.unique():
        fips_df = pop_df[pop_df.FIPS == fips]
        pop_dict[fips] = fips_df.Population.iloc[0]
    dataframe['Population'] = dataframe.FIPS.map(pop_dict)
        
    # Adding Vacant Units Columns
    vac_df = county_vacancy_df[county_vacancy_df.Year == year-2]
    owned_dict = {}
    rent_dict = {}
    for fips in vac_df.FIPS.unique():
        fips_df = vac_df[vac_df.FIPS == fips]
        owned_dict[fips] = fips_df.Sold_Vacant.iloc[0]
        rent_dict[fips] = fips_df.Rental_Vacant.iloc[0]
    dataframe['Vacant_Owned_Units_raw'] = dataframe.FIPS.map(owned_dict)
    dataframe['Vacant_Rental_Units_raw'] = dataframe.FIPS.map(rent_dict)
        
    dataframe['Total_Owned'] = dataframe.Owner_Occupied_Units + dataframe.Vacant_Owned_Units_raw
    dataframe['Total_Rented'] = dataframe.Renter_Occupied_Units + dataframe.Vacant_Rental_Units_raw
    dataframe['Total_Units'] = dataframe.Total_Owned + dataframe.Total_Rented
    dataframe['Residents_Per_Unit'] = round(dataframe.Population / dataframe.Total_Units, 2)
    dataframe['Vacant_Owned_Units_Percent'] = round(dataframe.Vacant_Owned_Units_raw / dataframe.Total_Owned, 3) * 100
    dataframe['Vacant_Rental_Units_Percent'] = round(dataframe.Vacant_Rental_Units_raw / dataframe.Total_Rented, 3) * 100
    dataframe['Vacant_Total_Units_Percent'] = round(dataframe.Vacant_Owned_Units_raw + dataframe.Vacant_Rental_Units_raw, 3) / dataframe.Total_Units * 100
    dataframe['Owned_Units_Percent'] = round(dataframe.Total_Owned / dataframe.Total_Units, 3) * 100
    dataframe['Rent_Units_Percent'] = round(dataframe.Total_Rented / dataframe.Total_Units, 3) * 100
    
    dataframe = dataframe.drop(['Vacant_Owned_Units_raw', 'Vacant_Rental_Units_raw'], axis=1)
    dataframe = dataframe[dataframe.Rent_Share_Inc < 50]  # Removing a few outliers that have too big an influence on choropleth map colors
    dataframe = dataframe[~((dataframe.Mort_Share_Inc > 50) & (dataframe.Total_Units < 10000))]  # Excluding outliers (a few low pop counties from each year)    
    master_df = pd.concat([master_df, dataframe])    
    counter += 1
    
# Adding Land Area Column
area_dict = {}
for fips in county_area_df.FIPS.unique():
    fips_df = county_area_df[county_area_df.FIPS == fips]
    area_dict[fips] = fips_df.Land_Area_sqm.iloc[0]

master_df['Area'] = master_df.FIPS.map(area_dict)
master_df['Housing_Den'] = round(master_df.Total_Units / master_df.Area, 1)
master_df['Pop_Den'] = round(master_df.Population / master_df.Area, 1)

master_df[master_df.Year == 2016].to_csv('county_rent_mort_inc_units_5yr_2018' + '.csv', index=False)
master_df.to_csv('county_rent_mort_inc_units_5yr.csv', index=False)