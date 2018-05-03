import pandas as pd
import numpy as np
import os

#%%
geo_audited = pd.read_excel('/usr/local/etc/ml/audited/Geography_audited.xlsx').fillna('')
geo_not_audited = pd.read_excel('/usr/local/etc/ml/audited/Geography_not_audited.xlsx').fillna('')
geo_audited['Geography'] = geo_audited['Geography'].apply(lambda x: x.strip('\n'))

#%% bins the data into US and non-US
geo_audited['US'] = geo_audited['Geography'].apply(lambda x: 'Y' if x == 'United States' else 'N')
geo_not_audited['US'] = geo_not_audited['Geography'].apply(lambda x: 'Y' if x == 'United States' else 'N')

#%%
africa = [
        'Africa',
        'Chad',  'Mozambique', 
       'Nigeria', 'South Africa', 
        'Botswana', 
        "Cote d'Ivoire", 
       'Morocco',
       'Tanzania',  'Zimbabwe', 
       'Rwanda',
       'Uganda', 'Zambia',
       'Democratic Republic of the Congo',
       'Liberia',
       'Somalia', 'Ethiopia',
       'Mauritania', 'Mali', 'Swaziland', 
       'Lesotho', 'Malawi', 'Angola', 'Congo',
        'Ghana', 'Algeria',
        'Djibouti',
]

middle_east = [
  'Bahrain',
  'Israel',
  'Turkey', 
  'Egypt', 
  'Middle East',
  'Oman', 'United Arab Emirates',
  'Saudi Arabia', 'Syria',
  'Iraq',
  'Pakistan', 
  'Afghanistan',  'Iran', 'Jordan',
  'Kuwait', 'Uzbekistan',  'Qatar'
]

asia = [
  'Japan',
  'India',
  'China',
  'Hong Kong',
  'Indonesia',
  'South Korea', 'Asia', 'Singapore',
  'Philippines',
  'Taiwan',
  'North Korea',
  'Nepal','Thailand',
  'Vietnam', 
  'Bangladesh',
  'Malaysia', 'Cambodia',
  'Bhutan', 'Myanmar',
  'Sri Lanka',
  'Azerbaijan',
  'Korea', 'Kyrgyzstan',
  'East & Southeast Asia', 'Brunei','Mongolia'
]

north_america = [
  'United States',
  'Canada',
  'Samoa',
  'Manitoba', 
  'Puerto Rico'
]

latin_america_and_caribbean = [
  'Argentina',
  'Latin America',
  'Brazil',
  'Chile',
  'Costa Rica',
  'Bermuda',
  'Colombia', 
  'West Indies', 'Caribbean',
  'Guatemala',
  'Venezuela',
  'Togo', 
  'Central America',
  'Dominican Republic',
  'Belize',
  'Honduras', 'Uruguay', 'Ecuador', 
  'Nicaragua',
  'Bahamas','El Salvador',
  'Bolivia', 
  'Cuba', 'Haiti',
  'Jamaica', 
  'South America','Paraguay','Peru','Mexico'
]

oceania = [
  'Fiji', 
  'Oceania', 
  'Papua New Guinea',
  'Pacific Islands',
  'Australia',
  'New Zealand'
]

europe = [
  'France',  'Denmark',
  'Europe',    'Spain', 'United Kingdom',
  'Germany', 'Switzerland', 'Sweden', 
  'Scandinavia',  'Netherlands', 
  'Russia',
  'Italy', 
  'Belgium', 
  'Ireland', 
  'Czech Republic', 
  'USSR', 
  'Poland', 
  'Finland',
  'Greece','Slovakia', 'Latvia',  'Iceland', 
  'Georgia (Republic of Georgia)', 
  'Norway', 'Austria','Serbia',  
  'Hungary', 
  'Croatia', 
  'Cyprus',
  'Estonia', 
  'Ukraine', 
  'Portugal', 'Slovenia', 'Romania', 
  'West Germany', 
  'Bulgaria',
  'Baltic states'
]

geo_dict = {}
for g in africa:
    geo_dict[g] = 'Africa'

for g in middle_east:
    geo_dict[g] = 'Middle East'

for g in asia:
    geo_dict[g] = 'Asia'
    
for g in north_america:
    geo_dict[g] = 'North America'
    
for g in latin_america_and_caribbean:
    geo_dict[g] = 'Latin America and Caribbean'
    
for g in oceania:
    geo_dict[g] = 'Oceania'

for g in europe:
    geo_dict[g] = 'Europe'

geo_not_audited['Region'] = geo_not_audited['Geography'].map(geo_dict)
geo_audited['Region'] = geo_audited['Geography'].map(geo_dict)
#%%
geo_not_audited_final =  geo_not_audited[
    (geo_not_audited['US'] == 'N') & 
    (geo_not_audited['Geography'] != '') &
    (geo_not_audited['Geography'] != 'Regions')
]

geo_audited_final =  geo_audited[
    (geo_audited['US'] == 'N') & 
    (geo_audited['Geography'] != '') &
    (geo_audited['Geography'] != 'Regions')
]

#%%
us_not_audited_final =  geo_not_audited[
    (geo_not_audited['Geography'] != '') &
    (geo_not_audited['Geography'] != 'Regions') &
    (geo_not_audited['Region'].isnull() == False)
]

us_audited_final =  geo_audited[
    (geo_audited['Geography'] != '') &
    (geo_audited['Geography'] != 'Regions') &
    (geo_audited['Region'].isnull() == False)
]

#%% exports data
if 'final' not in os.listdir('/usr/local/etc/ml/audited/'):
    os.mkdir('/usr/local/etc/ml/audited/final')

geo_audited_final.to_excel('/usr/local/etc/ml/audited/final/geo_audited_final.xlsx')
geo_not_audited_final.to_excel('/usr/local/etc/ml/audited/final/geo_not_audited_final.xlsx')

us_audited_final.to_excel('/usr/local/etc/ml/audited/final/us_audited_final.xlsx')
us_not_audited_final.to_excel('/usr/local/etc/ml/audited/final/us_not_audited_final.xlsx')
