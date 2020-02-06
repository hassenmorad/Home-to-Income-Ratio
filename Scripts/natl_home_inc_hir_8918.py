# Calculating Annual National HIR
import pandas as pd
import numpy as np
import array

# Annual National Median Income (Census summary)
natl_med_inc = pd.read_excel('h06ar.xls', skiprows=5, usecols=[0,2])[:32]  # Source: https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html (Table H-6)
natl_med_inc.columns = ['Year', 'Med_Inc']
natl_med_inc = natl_med_inc.drop([2,7])  # Dropping old/adjusted figures
natl_med_inc.Year = natl_med_inc.Year.astype(str)
natl_med_inc.Year = natl_med_inc.Year.apply(lambda x:x[:4])
natl_med_inc.Year = natl_med_inc.Year.astype(int)
natl_med_inc.Med_Inc = natl_med_inc.Med_Inc.astype(int)
natl_med_inc = natl_med_inc[::-1]

#-------------------------------------------------------------------------------------------------------------------------------------#
# Annual National Median Home Price (Zillow)
zillow_us = pd.read_csv('Metro_Zhvi_AllHomes.csv', usecols=list(range(5, 270,12)))  # Source: https://www.zillow.com/research/data/ (ZHVI All Homes - Metro & US - June prices)
zillow_us.columns = list(range(1996,2019))
zillow_us = zillow_us.iloc[0]
zillow9618 = list(zillow_us.values.astype(int))
zillow_us_df = pd.DataFrame({'Year':range(1996,2019), 'Med_Home':zillow9618})

#-------------------------------------------------------------------------------------------------------------------------------------#
# Median Home Price (FHFA- 1989-1995) *Will merge w/ Zillow data 
fhfa_df = pd.read_csv('county_home_inc_hir_8918.csv')
units8918 = pd.read_csv('county_housing_units_8918.csv')
natl_meds_dict = {}
for year in range(1989, 1997):
    yr_df = fhfa_df[fhfa_df.Year == year]
    yr_fips = yr_df.FIPS.unique()
    yr_lst = array.array('i')
    for fips in yr_fips:
        fips_df = yr_df[yr_df.FIPS == fips]
        price = fips_df.Med_Home.iloc[0]
        count = units8918[str(year)][units8918.FIPS == fips].iloc[0]
        yr_lst.extend(np.full(count, price))
    natl_meds_dict[year] = pd.Series(yr_lst).median()

# Adjusting FHFA values according to diff w/ 1996 FHFA & Zillow values
fhfa8996 = natl_meds_dict.values()
diff96 = zillow_us_df.Med_Home[zillow_us_df.Year == 1996][0] / natl_meds_dict[1996]
nat_home8995 = pd.DataFrame({'Year':range(1989, 1996), 'Med_Home':[round(i*diff96,0) for i in fhfa8996][:-1]})
nat_home = pd.concat([nat_home8995, zillow_us_df])

#-------------------------------------------------------------------------------------------------------------------------------------#   
# Merging Home Price w/ Income Data & Calculating HIR
nat_home['Med_Inc'] = natl_med_inc['Med_Inc'].values
nat_home['HIR'] = round(nat_home.Med_Home / nat_home.Med_Inc, 2)

nat_home.to_csv('natl_home_inc_hir_8918.csv', index=False)