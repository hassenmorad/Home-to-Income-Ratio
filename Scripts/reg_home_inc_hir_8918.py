# Calculating regional median HIRs (from county data)
# Note: Census data is available but only contains 1-yr estimates back to 2010
import pandas as pd
import numpy as np
import array

county_hir_df = pd.read_csv('county_home_inc_hir_8918.csv')

state_fips = pd.read_csv('50 States FIPS.txt', sep='\t')
state_fips.FIPS = state_fips.FIPS.astype(str).apply(lambda x:x.zfill(2))

state_dict = {}
for state in state_fips.State:
    abbrev = state_fips.Abbrev[state_fips.State == state].iloc[0]
    state_dict[state] = abbrev

#---------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Categorizing states into respective regions
units8918 = pd.read_csv('county_housing_units_8918.csv')
units8918['state_abbrev'] = units8918.State.map(state_dict)

# Source: https://www.bls.gov/cex/csxgeography.htm (I left DE, MD, & DC in Northeast since that seems to be the accepted region in other sources as well- bizarrely)
regions_dict = {'Northeast':['NJ', 'PA', 'NY', 'RI', 'CT', 'MA', 'VT', 'NH', 'ME'], 
                'Midwest':['ND', 'SD', 'NE', 'KS', 'MO', 'IA', 'MN', 'WI', 'MI', 'IL', 'IN', 'OH'], 
                'South':['TX', 'OK', 'AR', 'LA', 'MS', 'AL', 'GA', 'FL', 'SC', 'NC', 'VA', 'WV', 'KY', 'TN', 'DC', 'MD', 'DE'], 
                'West':['AK', 'HI', 'WA', 'OR', 'CA', 'NV', 'AZ', 'NM', 'CO', 'UT', 'WY', 'MT', 'ID']}

reversed_reg_dict = {}
for region in regions_dict:
    states = regions_dict[region]
    for state in states:
        reversed_reg_dict[state] = region

units8918['Region'] = units8918.state_abbrev.map(reversed_reg_dict)
county_hir_df['Region'] = county_hir_df.State.map(reversed_reg_dict)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Extracting median home price & income for each region (and calculating median HIR)
mig = pd.read_csv('irs_mig_91to2018.csv')
mig.Households = mig.Households.astype(int)  # Indicates # of households (to calculate median income)

#yr_reg_dict = {}
all_yrs_df = pd.DataFrame()
for year in range(1989, 2019):
    print(year)
    reg_dict = {}
    for region in units8918.Region.unique():
        df = county_hir_df[(county_hir_df.Year == year) & (county_hir_df.Region == region)]
        if year in [1989, 1990]:
            yr = 1991  # Assigning counts for households from 1991 (since 1991 is the first year data is available)
        else:
            yr = year  # yr called in line 60
        yr_reg_fips = df.FIPS.unique()
        yr_reg_home_lst = array.array('i')
        yr_reg_inc_lst = array.array('i')
        type_dict = {}
        for fips in yr_reg_fips:
            fips_df = df[df.FIPS == fips]
            home = fips_df.Med_Home.iloc[0]
            inc = fips_df.Med_Inc.iloc[0]
            home_units = units8918[str(year)][units8918.FIPS == fips].iloc[0]
            households = mig.Households[(mig.FIPS == fips) & (mig.Year == yr)].iloc[0]
            yr_reg_home_lst.extend(np.full(home_units, home))
            yr_reg_inc_lst.extend(np.full(households, inc))
        type_dict['Home'] = pd.Series(yr_reg_home_lst).median()
        type_dict['Income'] = pd.Series(yr_reg_inc_lst).median()
        #type_dict['HIR'] = round(type_dict['Home'] / type_dict['Income'], 2)
        reg_dict[region] = type_dict
    yr_df = pd.DataFrame(reg_dict).transpose()
    all_yrs_df = pd.concat([all_yrs_df, yr_df])
    #yr_reg_dict[year] = reg_dict

all_yrs_df['Region'] = list(reg_dict.keys()) * 30
yrs_col = list(range(1989,2019)) * 4
yrs_col.sort()
all_yrs_df['Year'] = yrs_col
all_yrs_df = all_yrs_df.sort_values(['Year', 'Region'])

# Including Census summary income data instead of manually collected
reg_incs = pd.read_csv('reg_incs_census_summary.csv')
all_yrs_df['Income'] = reg_incs.Med_Inc.values
all_yrs_df['HIR'] = all_yrs_df.Home / all_yrs_df.Income

all_yrs_df.to_csv('reg_home_inc_hir_8918.csv', index=False)

"""all_homes = []
all_incs = []
#all_hirs = []
for year in yr_reg_dict:
    regs = yr_reg_dict[year].keys()
    homes = []
    incs = []
    #hirs = []
    for reg in regs:
        homes.append(yr_reg_dict[year][reg]['Home'])
        incs.append(yr_reg_dict[year][reg]['Income'])
        #hirs.append(yr_reg_dict[year][reg]['HIR'])
    all_homes.append(homes)
    all_incs.append(incs)
    #all_hirs.append(hirs)

#reg_homes_df = pd.DataFrame(all_homes, columns=['South', 'West', 'Northeast', 'Midwest'])
#reg_incs_df = pd.DataFrame(all_incs, columns=['South', 'West', 'Northeast', 'Midwest'])
#reg_hirs_df = pd.DataFrame(all_hirs, columns=['South', 'West', 'Northeast', 'Midwest'])

master_df = pd.DataFrame()
data_strs = ['Home', 'Inc']
counter = 0
for lst in [all_homes, all_incs]:
    df = pd.DataFrame(lst, columns=['South', 'West', 'Northeast', 'Midwest'])
    values = []
    for col in df.columns:
        values += list(df[col].values)
    master_df[data_strs[counter]] = values
    counter += 1
    
#master_df['Hir'] = master_df.Home / master_df.Inc
#print(len(master_df))
#print(master_df.head(2))
#master_df['Year'] = list(range(1989,2019))*4
#master_df.to_csv('reg_home_inc_hir_chart_8918.csv', index=False)

reg_homes_df['Year'] = range(1989,2019)
reg_incs_df['Year'] = range(1989,2019)
reg_hirs_df['Year'] = range(1989,2019)
reg_homes_df.to_csv('reg_homes_8918.csv', index=False)
reg_incs_df.to_csv('reg_incs_8918.csv', index=False)
reg_hirs_df.to_csv('reg_hirs_8918.csv', index=False)

# Creating separate file for Altair chart
values = []
for col in reg_hirs_df.columns:
    values += list(reg_hirs_df[col].values)

reg_df = pd.DataFrame({'Year':list(range(1989,2019))*4, 'Region':['South']*30 + ['West']*30 + ['Northeast']*30 + ['Midwest']*30, 'HIR':values})
reg_df.to_csv('reg_hirs_chart_8918.csv', index=False)  # For Altair line chart"""
