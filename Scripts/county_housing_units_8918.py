# County housing unit counts (1989-2018)
import pandas as pd
import numpy as np
import array

# Source: https://www.census.gov/data/datasets/time-series/demo/popest/2010s-total-housing-units.html
# Data covers 2010-2018 (will calculate estimated counts from 1989-2009 below)
units = pd.read_csv('PEP_2018_PEPANNHU_with_ann.csv', encoding='latin', usecols=[1,2,5,6,7,8,9,10,11,12,13], skiprows=1)
units.columns = ['FIPS', 'County', 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]
units.FIPS = units.FIPS.astype(int)

# Calculating estimated housing units (1989-2009)
avg_chgs_dict = {}
for fips in units.FIPS.unique():
    series = units[units.FIPS == fips].values.tolist()[0][2:]
    change = pd.Series(series).pct_change().mean()
    avg_chgs_dict[fips] = change

units8909_dict = {}
for fips in units.FIPS.unique():
    first = units[2010][units.FIPS == fips].iloc[0]
    avg_chg = avg_chgs_dict[fips]
    units8909 = []
    for i in range(1989, 2010):
        new = round(first - first * avg_chg, 0)
        units8909.append(int(new))
        first = new
    units8909_dict[fips] = units8909[::-1]

units8909_df = pd.DataFrame.from_dict(units8909_dict).transpose()
units8909_df.columns = range(1989,2010)
units8909_df['FIPS'] = units8909_df.index

# Merging estimated units (1989-2009) w/ known units
units8918 = pd.merge(units[['FIPS', 'County']], units8909_df)
units8918 = pd.merge(units8918, units.drop('County', axis=1))
units8918[['County','State']] = units8918.County.str.split(', ', expand=True)

units8918.to_csv('county_housing_units_8918.csv', index=False)