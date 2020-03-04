# Regional median home values- combining Zillow & IRS tax return data for all zip codes
import pandas as pd
import numpy as np
import array

zillow = pd.read_csv('Zip_Zhvi_AllHomes.csv', encoding='latin', usecols=([1,3] + list(range(9, 274,12))))
zillow.columns = ['Zip', 'State'] + list(range(1996,2019))

zip04 = pd.read_csv('irs_zip_returns_9804.csv')
zip08 = pd.read_csv('irs_zip_returns_0508.csv')
zip17 = pd.read_csv('irs_zip_returns_0917.csv')

combined = pd.concat([zip04, zip08])
combined = pd.concat([combined, zip17])
combined = combined.sort_values(['Zip', 'Year'])

"""# Filling in missing household counts from IRS data (based on # of tax returns)
complete_zips_df = pd.DataFrame()
for zipcode in combined.Zip.unique():
    zip_df = combined[combined.Zip == zipcode]
    state = zip_df.State.iloc[0]
    missing_yrs = []
    for year in range(1996, 2019):
        if year not in zip_df.Year.unique():
            missing_yrs.append(year)
    missing_df = pd.DataFrame({'Year':missing_yrs, 'State':[state]*len(missing_yrs), 
                               'Zip':[zipcode]*len(missing_yrs), 'Returns':[np.nan]*len(missing_yrs)})
    complete_df = pd.concat([zip_df, missing_df]).sort_values('Year')
    complete_df = complete_df.fillna(method='bfill').fillna(method='ffill')
    complete_zips_df = pd.concat([complete_zips_df, complete_df])

complete_zips_df.to_csv('irs_returns_complete_9618.csv', index=False)"""
complete_zips_df = pd.read_csv('irs_returns_complete_9618.csv')
# Including Zip codes containing data for both IRS returns & Zillow home price
yr_zips_dict = {}
for year in range(1996, 2019):
    include_zips = []
    zil_yr = zillow[['Zip', year]].dropna()  # Excluding missing zip codes
    irs_yr_zips = complete_zips_df.Zip[complete_zips_df.Year == year].values
    for zipcode in zil_yr.Zip.values:
        if zipcode in irs_yr_zips:
            include_zips.append(zipcode)
    yr_zips_dict[year] = include_zips

# Organizing zip codes by region (to assign to Zillow zip codes)
regions_dict = {'Northeast':['NJ', 'PA', 'NY', 'RI', 'CT', 'MA', 'VT', 'NH', 'ME'], 
                'Midwest':['ND', 'SD', 'NE', 'KS', 'MO', 'IA', 'MN', 'WI', 'MI', 'IL', 'IN', 'OH'], 
                'South':['TX', 'OK', 'AR', 'LA', 'MS', 'AL', 'GA', 'FL', 'SC', 'NC', 'VA', 'WV', 'KY', 'TN', 'DC', 'MD', 'DE'], 
                'West':['AK', 'HI', 'WA', 'OR', 'CA', 'NV', 'AZ', 'NM', 'CO', 'UT', 'WY', 'MT', 'ID']}

reversed_reg_dict = {}
for region in regions_dict:
    states = regions_dict[region]
    for state in states:
        reversed_reg_dict[state] = region

zillow['Region'] = zillow.State.map(reversed_reg_dict)

# Calculating region median home price based on available median home prices in each zip code (weighted by # of households)
reg_means_df = pd.DataFrame()
for year in range(1996, 2019):
    zil_yr = zillow[['Zip', 'Region', year]][zillow.Zip.isin(yr_zips_dict[year])].dropna()
    reg_means = []
    for region in zillow.Region.unique():
        zil_reg = zil_yr[zil_yr.Region == region]
        reg_array = array.array('i')
        for zipcode in zil_reg.Zip.unique():
            zil_zip = zil_reg[zil_reg.Zip == zipcode]
            home_price = zil_zip[year].iloc[0]
            households = complete_zips_df.Returns[(complete_zips_df.Year == year) & (complete_zips_df.Zip == zipcode)].iloc[0]
            reg_array.extend(np.full(households, int(home_price)))
        reg_means.append(np.median(reg_array))
    yr_df = pd.DataFrame({'Year':[year]*4, 'Region':zillow.Region.unique(), 'Med_Home':reg_means})
    print(yr_df)
    reg_means_df = pd.concat([reg_means_df, yr_df])

reg_means_df.to_csv('irs_zillow_reg_med_home_9618.csv', index=False)

"""num_years = len(combined.Year.unique())
complete = []
#sevenplus = []

for zipcode in combined.Zip.unique():
    df = combined[combined.Zip == zipcode]
    if len(df) == num_years:  # Zip codes w/ no missing data
        complete.append(zipcode)
    elif len(df) > 6:
        sevenplus.append(zipcode)
        

complete_df = combined[combined.Zip.isin(complete)]
complete_df.to_csv('irs_zip_returns_9817_complete.csv', index=False)

incomplete_df = combined[~combined.Zip.isin(complete)]
incomplete_df.to_csv('irs_zip_returns_9817_incomplete.csv', index=False)

incomplete_7plus_df = combined[combined.Zip.isin(sevenplus)]
incomplete_7plus_df.to_csv('irs_zip_returns_9817_incomplete_7plus.csv', index=False)"""