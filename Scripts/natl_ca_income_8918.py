# Annual median incomes- nationally and CA
import pandas as pd
import numpy as np

natl_meds = pd.read_excel('h06ar.xls', skiprows=5, usecols=[0,2])[:32]  # Source: https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html (Table H-6)
natl_meds.columns = ['Year', 'Med_Inc']
natl_meds = natl_meds.drop([2,7])  # Dropping old/adjusted figures
natl_meds.Year = natl_meds.Year.astype(str)
natl_meds.Year = natl_meds.Year.apply(lambda x:x[:4])
natl_meds.Year = natl_meds.Year.astype(int)
natl_meds.Med_Inc = natl_meds.Med_Inc.astype(int)
natl_meds = natl_meds[::-1]

ca_meds = pd.read_excel('h08.xls', skiprows=4, usecols=([0,1,3,7,9,11,13] + list(range(17,64,2))))[:10]  # Source: https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html (Table H-8)
ca_inc8918 = ca_meds.iloc[6].values.tolist()[1:][::-1]
ca_incs = pd.DataFrame({'Year':range(1989, 2019), 'CA_Med_Inc':ca_inc8918})

natl_meds.to_csv('natl_income_8918.csv', index=False)
ca_incs.to_csv('ca_income_8918.csv', index=False)
