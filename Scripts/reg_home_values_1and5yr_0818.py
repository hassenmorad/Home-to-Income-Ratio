# Regional median home values (from Census 1-yr and 5-yr estimates)
import pandas as pd
import numpy as np
import os

names = ['1yr_1018', '5yr_0816']
yr_files = [os.listdir('Region Home Vals')[:25:3], os.listdir('Region Home Vals')[27:-1:3]]
counter = 0
for files in yr_files:
    master_df = pd.DataFrame()
    for file in files:
        year = int(file[7:11])
        data_df = pd.read_csv('Region Home Vals/' + file, usecols=[1,2])[1:]
        data_df.columns = ['Region', 'Home_Value']
        data_df.Region = data_df.Region.apply(lambda x:x.split(' ')[0])
        data_df['Year'] = [year] * 4
        master_df = pd.concat([master_df, data_df])

    master_df.to_csv('reg_home_values_' + names[counter] + '.csv', index=False)
    counter += 1