# Rent share of income by population density
import pandas as pd
import numpy as np
import array

file = pd.read_csv('county_rent_mort_inc_units_1yr.csv')

yrs_dict = {}
for year in range(2010, 2019):
    print(year)
    yr_df = file[file.Year == year].dropna(subset=['Housing_Den'])
    yr_df.Total_Rented = yr_df.Total_Rented.astype(int)
    
    # FIPS grouped by county population density
    county1k = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Pop_Den > 1000)].values
    county250 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Pop_Den > 250) & (yr_df.Pop_Den <= 1000)].values
    county100 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Pop_Den > 100) & (yr_df.Pop_Den <= 250)].values
    county50 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Pop_Den > 50) & (yr_df.Pop_Den <= 100)].values
    county25 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Pop_Den > 25) & (yr_df.Pop_Den <= 50)].values
    county10 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Pop_Den > 10) & (yr_df.Pop_Den <= 25)].values
    countyless10 = yr_df.FIPS[yr_df.Pop_Den <= 10].values
    
    groups_dict = {}
    fips_groups = [county1k, county250, county100, county50, county25, county10, countyless10]
    groups = ['1000', '250', '100', '50', '25', '10', 'Less10']
    counter = 0
    for fips_group in fips_groups:
        fips_rent = array.array('f')
        for fips in fips_group:
            med_rent = yr_df.Med_Rent_Inc[yr_df.FIPS == fips].iloc[0]
            home_count = yr_df.Total_Rented[yr_df.FIPS == fips].iloc[0]
            fips_rent.extend(np.full(home_count, med_rent))
        groups_dict[groups[counter]] = np.median(fips_rent).round(3)
        counter += 1
    yrs_dict[year] = groups_dict

df = pd.DataFrame(yrs_dict)
df = df.transpose()
df.columns = ['More than 1000', '250 to 1000', '100 to 250', '50 to 100', '25 to 50', '10 to 25', 'Less than 10']
df['Year'] = list(range(2010, 2019))
df = df.melt(id_vars='Year', var_name='Pop', value_name='Med_Rent')
df.to_csv('renter_inc_by_pop_den_1yr_1018.csv', index=False)