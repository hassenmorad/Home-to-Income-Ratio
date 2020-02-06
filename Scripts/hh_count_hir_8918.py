# HIR by County Household Count
import pandas as pd
import numpy as np
import array

file = pd.read_csv('county_home_inc_hir_8918.csv')
mig = pd.read_csv('irs_mig_91to2018.csv')

yrs_dict = {}
for year in range(1989, 2019):
    print(year)
    if year in [1989, 1990]:
        yr = 1991
    else:
        yr = year
        
    yr_df = file[file.Year == year]
    yr_fips = yr_df.FIPS.unique()
    mig_yr = mig[(mig.Year == yr) & (mig.FIPS.isin(yr_fips))]
    
    # FIPS grouped by county size
    county500k = mig_yr.FIPS[mig_yr.Households > 500000].values
    county200k = mig_yr.FIPS[mig_yr.Households > 200000].values
    county100k = mig_yr.FIPS[mig_yr.Households > 100000].values
    county50k = mig_yr.FIPS[mig_yr.Households > 50000].values
    county20k = mig_yr.FIPS[mig_yr.Households > 20000].values
    county10k = mig_yr.FIPS[mig_yr.Households > 10000].values
    countyless10k = mig_yr.FIPS[mig_yr.Households <= 10000].values
    
    groups_dict = {}
    fips_groups = [county500k, county200k, county100k, county50k, county20k, county10k, countyless10k]
    groups = ['500', '200', '100', '50', '20', '10', 'Less10']
    counter = 0
    for fips_group in fips_groups:
        fips_hirs = array.array('f')
        for fips in fips_group:
            hir = yr_df.HIR[yr_df.FIPS == fips].iloc[0]
            hh_size = mig.Households[(mig.Year == yr) & (mig.FIPS == fips)].iloc[0]
            fips_hirs.extend(np.full(hh_size, hir))
        groups_dict[groups[counter]] = np.median(fips_hirs)
        counter += 1
    yrs_dict[year] = groups_dict

df = pd.DataFrame(yrs_dict)
df = df.transpose()
df.columns = ['More than 500', '200 to 500', '100 to 200', '50 to 100', '20 to 50', '10 to 20', 'Less than 10']

hirs = []
for col in df.columns:
    hirs += list(df[col].values)
    
types = []
for col in df.columns:
    types += [col]*30
    
hh_count_df = pd.DataFrame({'Year':list(range(1989, 2019))*7, 'HIR':hirs, 'HH_Count':types})

hh_count_df.to_csv('hh_count_hir_8918.csv', index=False)