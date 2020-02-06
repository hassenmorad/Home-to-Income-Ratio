# County median income (Census SAIPE- source: https://www.census.gov/programs-surveys/saipe/data/datasets.All.html)
import pandas as pd
import numpy as np
import os

# 1989-2002
dats = os.listdir('Med_Inc_SAIPE/')[-6:] + os.listdir('Med_Inc_SAIPE/')[:3]
dats_df = pd.DataFrame()
years = [1989, 1993, 1995] + list(range(1997, 2003))
counter = 0
for file in dats:
    df = pd.read_table('Med_Inc_SAIPE/' + file, sep='\s+', skiprows=1, usecols=[0,1,22,23,25], error_bad_lines=False)
    df.columns = ['State FIPS', 'County FIPS', 'Median HH Income', 'County', 'State']
    df['Year'] = np.full(len(df), years[counter])
    dats_df = pd.concat([dats_df, df])
    counter += 1
    
dats_df = dats_df.sort_values(['State FIPS', 'County FIPS'])
dats_df['State FIPS'] = dats_df['State FIPS'].astype(str).apply(lambda x:x.zfill(2))
dats_df['County FIPS'] = dats_df['County FIPS'].astype(str).apply(lambda x:x.zfill(3))
dats_df['FIPS'] = dats_df['State FIPS'] + dats_df['County FIPS']

# Changing Dade County (FL) code to updated Miami-Dade County code
dats_df.loc[dats_df.FIPS == '12025', 'FIPS'] = '12086'
dats_df.loc[dats_df.FIPS == '12086', 'County'] = 'Miami-Dade'
# Changing Skagway-Yakutat-Angoon County (AK) code to updated Skagway-Hoonah-Angoon County code
dats_df.loc[dats_df.FIPS == '02231', 'FIPS'] = '02232'
dats_df.loc[dats_df.FIPS == '02232', 'County'] = 'Skagway-Hoonah-Angoon'

dats_df['Median HH Income'] = dats_df['Median HH Income'].replace('.', np.nan).astype(float)
missing_fips89 = dats_df.FIPS[dats_df['Median HH Income'].isnull()].unique()
not_missingdf = dats_df[~((dats_df.FIPS.isin(missing_fips89)) & (dats_df.Year <= 1993))]
missingdf = dats_df[(dats_df.FIPS.isin(missing_fips89)) & (dats_df.Year <= 1993)]
missingdf['Median HH Income'] = missingdf['Median HH Income'].fillna(method='bfill')

dats_df = pd.concat([not_missingdf, missingdf]).sort_values(['FIPS', 'Year'])

# Adding rows for missing 1990-1992 records (assigning avg. of 1989 & 1993 incomes to 1991; then avg. of 89 & 91 to 90 and avg of 91 & 93 to 92)
dats91 = dats_df[dats_df.Year == 1993].copy()
dats91['Median HH Income'] = pd.Series()
dats91['Year'] = list(np.full(len(dats91), 1991))
dats_df = pd.concat([dats_df, dats91]).sort_values(['FIPS', 'Year'])
dats_df['Median HH Income'] = dats_df['Median HH Income'].replace('.', np.nan).astype(float)

# Assigning avg. of prev and following incomes
# Source: https://stackoverflow.com/questions/44032771/fill-cell-containing-nan-with-average-of-value-before-and-after
dats_df['Median HH Income'] = round(dats_df['Median HH Income'].fillna((dats_df['Median HH Income'].shift() + dats_df['Median HH Income'].shift(-1))/2), 0)

dats90 = dats_df[dats_df.Year == 1993].copy()
dats90['Median HH Income'] = pd.Series()
dats90['Year'] = list(np.full(len(dats90), 1990))

dats92 = dats_df[dats_df.Year == 1993].copy()
dats92['Median HH Income'] = pd.Series()
dats92['Year'] = list(np.full(len(dats92), 1992))

dats94 = dats_df[dats_df.Year == 1993].copy()
dats94['Median HH Income'] = pd.Series()
dats94['Year'] = list(np.full(len(dats94), 1994))

dats96 = dats_df[dats_df.Year == 1993].copy()
dats96['Median HH Income'] = pd.Series()
dats96['Year'] = list(np.full(len(dats96), 1996))

dats_df = pd.concat([dats_df, dats90])
dats_df = pd.concat([dats_df, dats92])
dats_df = pd.concat([dats_df, dats94])
dats_df = pd.concat([dats_df, dats96]).sort_values(['FIPS', 'Year'])

# These counties contain too many incomplete years (easier to remove altogether)
dats_df = dats_df[~dats_df.FIPS.isin(['15005', '51780'])]

# Assigning avg. of prev and following incomes to years missing data
dats_df['Median HH Income'] = round(dats_df['Median HH Income'].fillna((dats_df['Median HH Income'].shift() + dats_df['Median HH Income'].shift(-1))/2), 0)

dats_df = dats_df[dats_df['County FIPS'].astype(int) > 0]
dats_df['Med_Inc'] = dats_df['Median HH Income'].astype(int)
dats_df = dats_df[['Year', 'State', 'FIPS', 'Med_Inc']].reset_index(drop=True)

#------------------------------------------------------------------------------------------------------------------------#
# Replacing incorrect state abbrev & county names (some data was mixed up through extraction from .dat files)
# Source: https://www.census.gov/library/publications/2011/compendia/usa-counties-2011.html
counties = pd.read_excel('CLF01.xls', usecols=[0,1])[2:]
counties['STCOU'] = counties['STCOU'].astype(str).apply(lambda x:x.zfill(5))

areaname_dict = {}
for fips in counties['STCOU']:
    area = counties.Areaname[counties.STCOU == fips].iloc[0]
    areaname_dict[fips] = area
    
dats_df['Areaname'] = dats_df['FIPS'].map(areaname_dict)
dats_df.loc[dats_df.FIPS == '12086', 'Areaname'] = 'Miami-Dade, FL'  # County FIPS changed in 1997
dats_df['State'] = dats_df['Areaname'].str.split(',', expand=True)[1].str.strip()

#------------------------------------------------------------------------------------------------------------------------#
# 2003-2018

excels_df = pd.DataFrame()
years = range(2003, 2019)
counter = 0
for file in os.listdir('Med_Inc_SAIPE')[3:-6]:
    if years[counter] < 2005:
        skiprows = 1
    elif years[counter] < 2013:
        skiprows = 2
    else:
        skiprows = 3
    df = pd.read_excel('Med_Inc_SAIPE/' + file, skiprows=skiprows, usecols=[0,1,2,3,22])
    df.columns = ['State FIPS', 'County FIPS', 'State', 'County', 'Median HH Income']
    df['Year'] = np.full(len(df), years[counter])
    excels_df = pd.concat([excels_df, df])
    counter += 1
    
excels_df = excels_df[excels_df['County FIPS'] > 0]
excels_df['County FIPS'] = excels_df['County FIPS'].astype(int)
excels_df['State FIPS'] = excels_df['State FIPS'].astype(int).astype(str).apply(lambda x:x.zfill(2))
excels_df['County FIPS'] = excels_df['County FIPS'].astype(int).astype(str).apply(lambda x:x.zfill(3))
excels_df['FIPS'] = excels_df['State FIPS'] + excels_df['County FIPS']

excels_df = excels_df[excels_df.FIPS != '15005']
excels_df['Areaname'] = excels_df['FIPS'].map(areaname_dict)
excels_df['Med_Inc'] = excels_df['Median HH Income'].astype(int)

excels_df = excels_df[['Year', 'State', 'FIPS', 'Med_Inc', 'Areaname']].reset_index(drop=True)

#------------------------------------------------------------------------------------------------------------------------#
# Combining 89-02 w/ 03-18 income data
combined = pd.concat([dats_df, excels_df]).reset_index(drop=True)

# Fixing errors in state col
states_df = pd.read_csv('50 States FIPS.txt', sep='\t')
not_missing = combined[(combined.State.isin(states_df.Abbrev.values))]
missing_state = combined[(~combined.State.isin(states_df.Abbrev.values))]
rename_dict = {'02201':'AK', '02232':'AK', '02280':'AK', '11001':'DC'}
missing_state.State = missing_state.FIPS.map(rename_dict)

income_df = pd.concat([not_missing, missing_state]).sort_values(['Year', 'FIPS']).reset_index(drop=True)

income_df.to_csv('county_income_8918.csv', index=False)