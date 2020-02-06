# Calculating Annual California State Median HIR
import pandas as pd
import numpy as np
import array

# Median Income
ca_med_inc = pd.read_excel('h08.xls', skiprows=4, usecols=([0,1,3,7,9,11,13] + list(range(17,64,2))))[:10]  # Source: https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html (Table H-8)
ca_inc8918 = ca_med_inc.iloc[6].values.tolist()[1:][::-1]
ca_med_inc = pd.DataFrame({'Year':range(1989, 2019), 'Med_Inc':ca_inc8918})

#-------------------------------------------------------------------------------------------------------------------------------------#
# Median Home Price (Zillow- 1996-2018) *Zillow data is unavailable before 1996
zillow_st = pd.read_csv('State_Zhvi_AllHomes.csv', usecols=([1] + list(range(5, 270,12))))  # Source: https://www.zillow.com/research/data/ (ZHVI All Homes - State - June prices)
zillow_st.columns = ['State'] + list(range(1996,2019))
ca = zillow_st.iloc[0].tolist()[1:]
ca_home_df = pd.DataFrame({'Year':range(1996, 2019), 'Med_Home':ca})

#-------------------------------------------------------------------------------------------------------------------------------------#
# Median Home Price (FHFA- 1989-1995) *Will merge w/ Zillow data 
fhfa_df = pd.read_csv('county_home_inc_hir_8918.csv')
fhfa_df = fhfa_df[(fhfa_df.FIPS > 6000) & (fhfa_df.FIPS < 7000)]
units8918 = pd.read_csv('county_housing_units_8918.csv')
ca_meds_dict = {}
for year in range(1989, 1997):
    yr_df = fhfa_df[(fhfa_df.Year == year) & (fhfa_df.FIPS > 6000) & (fhfa_df.FIPS < 7000)]
    yr_fips = yr_df.FIPS.unique()
    yr_lst = array.array('i')
    for fips in yr_fips:
        fips_df = yr_df[yr_df.FIPS == fips]
        price = fips_df.Med_Home.iloc[0]
        count = units8918[str(year)][units8918.FIPS == fips].iloc[0]
        yr_lst.extend(np.full(count, price))
    ca_meds_dict[year] = int(pd.Series(yr_lst).median())
    
# Adjusting FHFA values according to diff w/ 1996 FHFA & Zillow values
fhfa8995 = ca_meds_dict.values()
diff96 = ca_home_df.Med_Home[ca_home_df.Year == 1996][0] / ca_meds_dict[1996]
ca_home8995 = pd.DataFrame({'Year':range(1989, 1996), 'Med_Home':[round(i*diff96,0) for i in fhfa8995][:-1]})
ca_home = pd.concat([ca_home8995, ca_home_df])

#-------------------------------------------------------------------------------------------------------------------------------------#
# Merging Home Price w/ Income Data & Calculating HIR
ca_home['Med_Inc'] = ca_med_inc['Med_Inc'].values
ca_home['HIR'] = round(ca_home.Med_Home / ca_home.Med_Inc, 2)

ca_home.to_csv('ca_state_home_inc_hir_8918.csv', index=False)