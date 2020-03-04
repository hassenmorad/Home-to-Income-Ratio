# Mortgage share of income by population density
import pandas as pd
import numpy as np
import array

file = pd.read_csv('county_rent_mort_inc_units_1yr.csv')

yrs_dict = {}
for year in range(2010, 2019):
    print(year)
    yr_df = file[file.Year == year].dropna(subset=['Housing_Den'])
    yr_df.Total_Owned = yr_df.Total_Owned.astype(int)
    
    # FIPS grouped by county population density
    homes75 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Housing_Den > 75)].values
    homes30 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Housing_Den > 30) & (yr_df.Housing_Den <= 75)].values
    homes20 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Housing_Den > 20) & (yr_df.Housing_Den <= 30)].values
    homes10 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Housing_Den > 10) & (yr_df.Housing_Den <= 20)].values
    homes5 = yr_df.FIPS[(yr_df.Year == year) & (yr_df.Housing_Den > 5) & (yr_df.Housing_Den <= 10)].values
    homesless5 = yr_df.FIPS[yr_df.Housing_Den <= 5].values
    
    groups_dict = {}
    fips_groups = [homes75, homes30, homes20, homes10, homes5, homesless5]
    groups = ['75', '30', '20', '10', '5', 'Less5']
    counter = 0
    for fips_group in fips_groups:
        fips_mort_share = array.array('f')
        for fips in fips_group:
            mort_share_inc = yr_df.Mort_Share_Inc[yr_df.FIPS == fips].iloc[0]
            home_count = yr_df.Total_Owned[yr_df.FIPS == fips].iloc[0]
            fips_mort_share.extend(np.full(home_count, mort_share_inc))
        groups_dict[groups[counter]] = np.median(fips_mort_share).round(3)
        counter += 1
    yrs_dict[year] = groups_dict

df = pd.DataFrame(yrs_dict)
df = df.transpose()
df.columns = ['More than 75', '30 to 75', '20 to 30', '10 to 20', '5 to 10', 'Less than 5']

mort_share = []
for col in df.columns:
    mort_share += list(df[col].values)
    
types = []
for col in df.columns:
    types += [col]*9  # Number of years
    
pop_den_df = pd.DataFrame({'Year':list(range(2010, 2019))*6, 'Mort_Share_Inc':mort_share, 'Home_Units':types})

pop_den_df.to_csv('mort_share_inc_by_hous_den_1yr_1018.csv', index=False)