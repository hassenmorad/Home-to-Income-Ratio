# County HIR
import pandas as pd
import numpy as np
import array

income = pd.read_csv('county_income_8918.csv')   # 1989-2018
income = income.sort_values(['Year', 'FIPS'])

house = pd.read_csv('county_home_prices8618.csv')  # 1975-2018 (most counties don't contain data back to 1975, though)
house = house[(house.FIPS != 8014) & (house.Year > 1988)].sort_values(['Year', 'FIPS'])

# Extracting income data to merge w/ home price df
incs = []
for year in range(1989, 2019):
    fips = list(house.FIPS[house.Year == year].values)
    inc_vals = list(income.Med_Inc[(income.Year == year) & (income.FIPS.isin(fips))].values)
    incs += (inc_vals)

house['Med_Inc'] = incs
house['Home_Inc_Ratio'] = round(house['Med_House_Price'] / house['Med_Inc'], 2)
house = house.sort_values(['FIPS', 'Year'])

# Adding pct_change column for HIR
hir_chgs = []
for fips in house.FIPS.unique():
    df = house[house.FIPS == fips]
    hir_chgs += df.Home_Inc_Ratio.pct_change().values.tolist()
house['HIR_Chg'] = hir_chgs

house.to_csv('county_home_inc_hir_8918.csv', index=False)