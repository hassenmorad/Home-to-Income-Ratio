# Annual Regional Income (Census)
import pandas as pd
import numpy as np

# Annual National Median Income (Census summary)
incs = pd.read_excel('h06ar.xls', skiprows=5, skipfooter=10, usecols=[0,2])  # Source: https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html (Table H-6)
incs.columns = ['Year', 'Med_Inc']
incs.Year = incs.Year.astype(str).apply(lambda x:x[:4])

master_df = pd.DataFrame()
northeast = incs.iloc[49:81]
midwest = incs.iloc[98:130]
south = incs.iloc[147:179]
west = incs.iloc[196:228]
regions_dict = {'Northeast':northeast, 'Midwest':midwest, 'South':south, 'West':west}
for region in regions_dict:
    reg_df = regions_dict[region].reset_index(drop=True)
    reg_df = reg_df.drop([2,7])  # Dropping old/adjusted figures
    reg_df.Year = reg_df.Year.astype(int)
    reg_df.Med_Inc = reg_df.Med_Inc.astype(int)
    reg_df['Region'] = list(np.full(len(reg_df), region))
    reg_df = reg_df[::-1]
    master_df = pd.concat([master_df, reg_df])
    
master_df = master_df.sort_values(['Year', 'Region'])
master_df.to_csv('reg_incs_census_summary.csv', index=False)