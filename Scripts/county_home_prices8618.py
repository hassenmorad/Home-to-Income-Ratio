import pandas as pd
import numpy as np

# House price data based on FHFA House Price Index
hpi_df = pd.read_excel('HPI_AT_BDL_county.xlsx', skiprows=6) # Source: https://www.fhfa.gov/PolicyProgramsResearch/Research/Pages/wp1601.aspx

# Replacing null HPI values w/ avg. of values before and after (if they exist- otherwise, values remain null)
hpi_df.HPI = hpi_df.HPI.replace('.', np.nan).astype(float)

hpi_df.HPI = hpi_df.HPI.fillna((hpi_df.HPI.shift() + hpi_df.HPI.shift(-1))/2) # Source: https://stackoverflow.com/questions/44032771/fill-cell-containing-nan-with-average-of-value-before-and-after

# Filling the remaining missing HPI cells w/ the next most recent HPI value (since the relevant missing HPIs are only from 2013 onwards, the HPI will be the most recent value from the same FIPS)
hpi_df.HPI = hpi_df.HPI.fillna(method='ffill')

# Adding county/state column (to displaying location via interactive hover map)
counties = pd.read_excel('CLF01.xls', usecols=[0,1])[2:]  # Source: https://www.census.gov/library/publications/2011/compendia/usa-counties-2011.html

areaname_dict = {}
for fips in counties['STCOU']:
    area = counties.Areaname[counties.STCOU == fips].iloc[0]
    areaname_dict[fips] = area
    
hpi_df['Areaname'] = hpi_df['FIPS code'].map(areaname_dict)

hpi_df = hpi_df.rename({'FIPS code': 'FIPS'}, axis=1)
hpi_df = hpi_df[['Year', 'State', 'FIPS', 'HPI', 'Areaname']]
hpi_df = hpi_df.sort_values(['FIPS', 'Year']).reset_index(drop=True)

#--------------------------------------------------------------------------------------------------#
# Converting HPI values to House Prices:
home_prices = pd.read_csv('ACS_16_5YR_Home_Prices.csv', skiprows=3, usecols=[4,6,7], encoding='latin')  # Source: https://factfinder.census.gov/ (searched for "Median Value of Owner-Occupied" in *advanced* search)
home_prices.columns = ['FIPS', 'County', 'Med_Price']
# 2016 median home prices (using this data instead of 2017 data since 25 records were missing 2017 HPIs, whereas 2016 was only missing 13)

home_prices = home_prices[home_prices.Med_Price != '-']  # Only two rows contained this filler value
home_prices['Med_Price'] = home_prices['Med_Price'].astype(int)

# Calculating annual home prices based on 2016 price & HPI
adj_prices = []
for fips in hpi_df.FIPS[hpi_df.Year == 2016].unique():
    hpi16 = hpi_df.HPI[(hpi_df.FIPS == fips) & (hpi_df.Year == 2016)].iloc[0]
    price16 = home_prices.Med_Price[home_prices.FIPS == fips].iloc[0]
    df = hpi_df[hpi_df.FIPS == fips]
    adj_prices += list(df['HPI'] / hpi16 * price16)
    
hpi_df['Med_House_Price'] = [int(round(x,0)) for x in adj_prices]

#--------------------------------------------------------------------------------------------------#
# Zillow House Price Data 
# (adding data for counties missing from hpi_df - additional 78 counties)
zillow = pd.read_csv('Zillow County Monthly.csv', usecols=[1,2,4,5] + list(range(15, 280, 12)), encoding='latin')  # Source: https://www.zillow.com/research/data/ (Home Values-ZHVI All Homes-County)
zillow['FIPS'] = (zillow.StateCodeFIPS.astype(str) + zillow.MunicipalCodeFIPS.astype(str).apply(lambda x:x.zfill(3))).astype(int)
zillow = zillow.drop(['StateCodeFIPS', 'MunicipalCodeFIPS'], axis=1)
zillow.columns = ['County', 'State'] + [str(yr) for yr in range(1996, 2019)] + ['FIPS']

zillowfips = list(zillow.FIPS.sort_values().values)
zillow_extra = []
for fips in zillowfips:
    if fips not in hpi_df.FIPS.unique():
        zillow_extra.append(fips)
        
# Calculating state avg. house price % change (to replace zillow records w/ less than 8 price values recorded, since a larger sample is needed for a more accurate estimate)
pct_chg_dict = {}
for state in hpi_df.State.unique():
    st_df = hpi_df[hpi_df.State == state]
    st_chgs = []
    for fips in st_df.FIPS.unique():
        fp_df = st_df[st_df.FIPS == fips]
        st_chgs.append(fp_df.HPI.pct_change().mean())
    pct_chg_dict[state] = sum(st_chgs) / len(st_chgs)
    
zillow_new = pd.DataFrame()

for fips in zillow_extra:
    new_prices = []
    df = zillow[zillow.FIPS == fips].dropna(axis=1)  # Only keeping cols of years w/ no nulls
    
    if len(df.columns) > 8:  # Excludes 4 FIPS (too few home price values to calculate accurate rate of price change)
        cols = df.columns[2:-1]  # (96-18 cols)
        prices = list(df[cols].iloc[0].astype(int).values)
        avg_chg = pd.Series(prices).pct_change().mean()
        earliest_price = df.iloc[0][2]  # 96 price or earliest yr available after
        earliest_yr = int(cols[0])
        missing_yrs = range(earliest_yr - 1, 1988, -1)  # earliest year to 1991 (backwards)
        state = df.State.iloc[0]
        
        if len(df.columns) < 11:  # i.e. 9 or 10
            avg_chg = pct_chg_dict[state]  # If not previously assigned above
        
        for yr in missing_yrs:
            new_earliest = int(round(earliest_price/(1 + avg_chg),0))
            new_prices.append(new_earliest)
            earliest_price = new_earliest
        new_prices.reverse()
        
        new_df = pd.DataFrame({'Year':range(1989, 2019), 'FIPS':list(np.full(30, fips)), 'Med_House_Price':(new_prices + prices)})
        zillow_new = pd.concat([zillow_new, new_df])
        
#--------------------------------------------------------------------------------------------------#
# Combining Zillow & FHFA data
no_HPI = hpi_df.drop('HPI', axis=1)
zillow_new['Areaname'] = zillow_new['FIPS'].map(areaname_dict)
zillow_new['State'] = [x.split(', ')[1] for x in zillow_new['Areaname'].values]
zillow_new = zillow_new[no_HPI.columns]
combined = pd.concat([no_HPI, zillow_new]).sort_values(['Year', 'FIPS']).reset_index(drop=True)

combined.to_csv('med_house_price_86to18.csv', index=False)