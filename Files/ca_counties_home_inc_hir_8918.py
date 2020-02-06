# Calculating Annual California Indiv. Counties HIR

import pandas as pd
import numpy as np
import array


# Zillow county median home prices (June prices: https://www.zillow.com/research/data/ - ZHVI All Homes - County)
zillow_county = pd.read_csv('Zillow County Monthly.csv', usecols=([1,2,4,5] + list(range(9, 274,12))))
zillow_county.columns = ['County','State','fips1', 'fips2'] + list(range(1996,2019))
zillow_county['FIPS'] = (zillow_county.fips1.astype(str) + zillow_county.fips2.astype(str).apply(lambda x:x.zfill(3))).astype(int)
zillow_county = zillow_county[['County','State', 'FIPS'] + list(range(1996,2019))]

# CA counties
zillow_ca = zillow_county[(zillow_county.FIPS > 6000) & (zillow_county.FIPS < 7000)]

house_prices = []
fips_col = []
for fips in zillow_ca.FIPS.unique():
    house_prices += zillow_ca[zillow_ca.FIPS == fips].values.tolist()[0][3:]
    fips_col += list(np.full(23, fips))  # 23 = len(range(1996,2019))
    
ca_counties_home_df = pd.DataFrame({'Year':list(range(1996,2019))*len(zillow_ca.FIPS.unique()), 'FIPS':fips_col, 'Med_Home':house_prices})

#-------------------------------------------------------------------------------------------------------------------------------------#
# Adding Income Data and Calculating HIR
county_home_inc_hir = pd.read_csv('county_home_inc_hir_8918.csv')
incomes = []
for fips in ca_counties_home_df.FIPS.unique():
    incomes += county_home_inc_hir.Med_Inc[(county_home_inc_hir.FIPS == fips) & (county_home_inc_hir.Year > 1995)].values.tolist()
    
ca_counties_home_df['Med_Inc'] = incomes
ca_counties_home_df['HIR'] = round(ca_counties_home_df.Med_Home / ca_counties_home_df.Med_Inc, 2)

# Removing pre-2004 values for this fips since it's missing (will add below)
ca_counties_home_df = ca_counties_home_df[~((ca_counties_home_df.Year < 2004) & (ca_counties_home_df.FIPS == 6033))]

#-------------------------------------------------------------------------------------------------------------------------------------#
# Merging 89-95 data from county_home_inc_hir_8918
fips8995 = ca_counties_home_df.FIPS.unique()
ca8995 = county_home_inc_hir[['Year', 'FIPS', 'Med_Home', 'Med_Inc', 'HIR']][(county_home_inc_hir.FIPS.isin(fips8995)) & (county_home_inc_hir.Year < 1996)]
fips6033 = county_home_inc_hir[['Year', 'FIPS', 'Med_Home', 'Med_Inc', 'HIR']][(county_home_inc_hir.Year < 2004) & (county_home_inc_hir.FIPS == 6033)]
ca8995 = pd.concat([fips6033, ca8995])
combined = pd.concat([ca8995, ca_counties_home_df]).sort_values(['FIPS', 'Year'])

combined.to_csv('ca_counties_home_inc_hir_8918.csv', index=False)