# Housing % of Income by County Household Count
import pandas as pd
import numpy as np
import array

hous_per = pd.read_csv('county_rent_vs_mort_and_inc_1yr.csv')
hh_counts = pd.read_csv('irs_mig_91to2018.csv')

master_df = pd.DataFrame()
for year in range(2010, 2019):
    print(year)
    per_df = hous_per[hous_per.Year == year].dropna(subset=['Rent_Share_Inc_dec'])
    per_fips = per_df.FIPS.unique()
    hh_df = hh_counts[(hh_counts.Year == year) & (hh_counts.FIPS.isin(per_fips))]
    
    # FIPS grouped by county size
    county500k = hh_df.FIPS[hh_df.Households >= 500000].values
    county200k = hh_df.FIPS[(hh_df.Households >= 200000) & (hh_df.Households < 500000)].values
    county100k = hh_df.FIPS[(hh_df.Households >=100000) & (hh_df.Households < 200000)].values
    county50k = hh_df.FIPS[(hh_df.Households >= 50000) & (hh_df.Households < 100000)].values
    county20k = hh_df.FIPS[(hh_df.Households >= 20000) & (hh_df.Households < 50000)].values
    county10k = hh_df.FIPS[(hh_df.Households >= 10000) & (hh_df.Households < 20000)].values
    countyless10k = hh_df.FIPS[hh_df.Households < 10000].values
    
    type_dict = {}
    rent_dict = {}
    mort_dict = {}
    fips_groups = [county500k, county200k, county100k, county50k, county20k, county10k, countyless10k]
    groups = ['500', '200', '100', '50', '20', '10', 'Less10']
    counter = 0
    for fips_group in fips_groups:
        fips_rent_pers = array.array('f')
        fips_mort_pers = array.array('f')
        for fips in fips_group:
            rent_per = per_df.Rent_Share_Inc_dec[per_df.FIPS == fips].iloc[0]
            mort_per = per_df.Mort_Share_Inc_dec[per_df.FIPS == fips].iloc[0]
            hh_count = hh_df.Households[hh_df.FIPS == fips].iloc[0]
            fips_rent_pers.extend(np.full(hh_count, rent_per))
            fips_mort_pers.extend(np.full(hh_count, mort_per))
        rent_dict[groups[counter]] = np.median(fips_rent_pers).round(3)
        mort_dict[groups[counter]] = np.median(fips_mort_pers).round(3)
        counter += 1
    type_dict['Rents'] = rent_dict
    type_dict['Morts'] = mort_dict
    
    df = pd.DataFrame(type_dict).transpose()
    master_df = pd.concat([master_df, df])
    
master_df.columns = ['More than 500', '200 to 500', '100 to 200', '50 to 100', '20 to 50', '10 to 20', 'Less than 10']
master_df['Type'] = master_df.index
yrs = list(range(2010, 2019)) * 2
yrs.sort()
master_df['Year'] = yrs
master_df.to_csv('hh_count_housing_per_inc_1yr_1018.csv', index=False)