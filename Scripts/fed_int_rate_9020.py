# Fed Interest Rate Data (Dates are approximate- representing the Sunday of the week when the rate was announced)
import pandas as pd
import numpy as np
from datetime import timedelta

file0319 = pd.read_html('https://www.federalreserve.gov/monetarypolicy/openmarket.htm')
file9002 = pd.read_html('https://www.federalreserve.gov/monetarypolicy/openmarket_archive.htm')

# DF containing all instances where the Fed released a new funds rate
rates_df = pd.DataFrame()
file2_yrs = list(range(1990,2003))[::-1]
file2_yrs.remove(1993)
years = [[2019, 2018, 2017, 2016, 2015, 2008, 2007, 2006, 2005, 2004, 2003], file2_yrs]
counter1 = 0
for file in [file0319, file9002]:
    counter2 = 0
    file_df = pd.DataFrame()
    for table in file:
        table['Year'] = list(np.full(len(table),years[counter1][counter2]))
        file_df = pd.concat([file_df, table])
        counter2 += 1
    rates_df = pd.concat([rates_df, file_df])
    counter1 += 1

rates_df['Date'] = rates_df['Date'] + ', ' + rates_df['Year'].astype(str)
rates_df['Date'] = pd.to_datetime(rates_df['Date'])
rates_df['Week_Num'] = rates_df['Date'].dt.week
rates_df['Target_Rate'] = rates_df['Level (%)'].astype(str).apply(lambda x:x.split('-')[-1]).astype(float)
rates_df['YrWk'] = rates_df['Year'].astype(str) + rates_df['Week_Num'].astype(str)
rates_df = rates_df.drop(['Increase', 'Decrease', 'Level (%)', 'Year'], axis=1)
rates_df = rates_df[::-1].reset_index(drop=True)

# Filling in weekly dates b/w dates in rates_df.Date to create a smooth x-axis time range for plotting
master_df = rates_df[['Date', 'Target_Rate']].head(1)
dates = rates_df.Date.values
counter = 1
for date in dates[:-1]:
    df = rates_df[rates_df.Date == date]
    rate = df.Target_Rate.iloc[0]
    next_date = pd.to_datetime(dates[counter])
    fill_dates = pd.date_range(pd.to_datetime(date), next_date, freq='W')
    fill_df = pd.DataFrame({'Date':fill_dates, 'Target_Rate':list(np.full(len(fill_dates),rate))})
    master_df = pd.concat([master_df, fill_df])
    counter += 1

master_df = pd.concat([master_df, rates_df[['Date', 'Target_Rate']].tail(1)])

master_df['Year'] = master_df.Date.dt.year
master_df['Week_Num'] = master_df.Date.dt.week
master_df['YrWk'] = master_df.Year.astype(str) + master_df.Week_Num.astype(str)
master_df = master_df.drop_duplicates(subset='YrWk', keep='last')
master_df = master_df.reset_index(drop=True)

# Adding last date and filling data up to today
today_rate = master_df.tail(1).Target_Rate.iloc[0]
last_date = master_df.tail(1).Date.iloc[0]
today_date = pd.to_datetime(pd.datetime.now().strftime("%Y-%m-%d"))
remaining_dates = pd.date_range(last_date, today_date, freq='W')

remaining_df = pd.DataFrame({'Date':remaining_dates, 'Target_Rate':list(np.full(len(remaining_dates), today_rate))})
remaining_df['Year'] = remaining_df.Date.dt.year
remaining_df['Week_Num'] = remaining_df.Date.dt.week
remaining_df['YrWk'] = remaining_df.Year.astype(str) + remaining_df.Week_Num.astype(str)

# Completed dataframe
combined_df = pd.concat([master_df, remaining_df]).drop_duplicates(subset='YrWk', keep='last')
combined_df = combined_df.drop(['Week_Num','YrWk'], axis=1).reset_index(drop=True)
combined_df.Target_Rate = combined_df.Target_Rate / 100

combined_df.to_csv('fed_int_rate_9020.csv', index=False)