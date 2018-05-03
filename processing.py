import pandas as pd
import re

#%%
from pim.pimdata import *
a = PimData()
products = a.products
relationships = a.relationships
contributors = a.contributors

#%% read cached xlsx file
df = pd.read_excel('/usr/local/etc/nltk/df.xlsx').fillna('')

#%% collapse text columns down to one, preferring EPUB-derived full text
def text_switch(row):
    if row['EPUB Text'] != '':
        return row['EPUB Text']
    else:
        return row['PDF Text']
        
df['Full Text'] = df.apply(text_switch,axis=1)
# df = df[['Product ID','Full Text']].copy()

#%%
def text_cleanup(string): # will need expansion
    string = ' '.join(string.split())
    strip_phrases = ['Harvard',
    'Harvard Business School',
    'Business School',
    'see Exhibit',
    'see exhibit'
    ]
    for p in strip_phrases:
        string = re.sub(p, '', string)
    if 'No part of this publication may be reproduced, stored in a retrieval system, used in a spreadsheet, or transmitted in any form or by any means—electronic, mechanical, photocopying, recording, or otherwise' in string:
        string = string.split('No part of this publication may be reproduced, stored in a retrieval system, used in a spreadsheet, or transmitted in any form or by any means—electronic, mechanical, photocopying, recording, or otherwise')[1]
    elif 'This publication may not be digitized, photocopied, or otherwise reproduced, posted, or transmitted, without the permission' in string:
        string = string.split('This publication may not be digitized, photocopied, or otherwise reproduced, posted, or transmitted, without the permission')[1]
    return re.sub('[\W_]--[ ]]+', '', string)

df['Full Text'] = df['Full Text'].apply(text_cleanup)
df = df[['Product ID','Full Text']]

#%%
mask = products[products['Product ID'].isin(df['Product ID'])].copy()

df = pd.merge(df,mask[['Product ID','Title','Major Discipline','Pre-Abstract','Abstract','Post-Abstract','Learning Objective Description','Course','Series 1','Series 2','Series 3','Major Subject','Taxonomy']],on='Product ID')
df = df.drop_duplicates(subset='Product ID')
# backup = df.copy()

#%% look up author information from the contributors data set
aus = relationships.loc[
    (relationships['Association Type'] == 'Contributors') & 
    (relationships['Role'] == 'AU')
]

def author(row):
    rel = aus.loc[aus['Base'] == row['Product ID']]
    if len(rel['Contributors']) > 0:
        a = list(rel['Contributors'])
    else:
        a = ''
    return a
df['Contributors'] = df.apply(author,axis=1)

#%%
df.rename(columns={'Contributors':'First Contributor'},inplace=True)
df['First Contributor'] = df['First Contributor'].apply(lambda x: [re.sub('[0-9]','',n) for n in x] if x != '' else '')
df['Second Contributor'] = df['First Contributor'].apply(lambda x: x[1] if len(x) > 1 else '')
df['Third Contributor'] = df['First Contributor'].apply(lambda x: x[2] if len(x) > 2 else '')
df['First Contributor'] = df['First Contributor'].apply(lambda x: x[0] if type(x) == list else str(x))

df['Full Abstract'] = df.apply(lambda x: ' '. join([x['Pre-Abstract'] + x['Abstract'] + x['Post-Abstract'] + x['Learning Objective Description']]),axis=1)
df.drop(['Pre-Abstract','Abstract','Post-Abstract','Learning Objective Description'],axis=1,inplace=True)
df['Full Abstract'] = df['Full Abstract'].apply(lambda x: '' if re.search('^Teaching note for',x) or re.search('^Teaching Note for',x) else x)

# backup2 = df.copy()

#%% define geography terms
df['Geography'] = df['Taxonomy'].apply(lambda x: [a for a in x.split('^') if 'Geography' in a])
df['Geography'] = df['Geography'].apply(lambda x: [s.split('Geography/')[1] for s in x] if len(x) != 0 else '')

def taxo_strip(t):
    if t != '':
        l = t.split('^')
        l = [x.strip() for x in l if 'Geography/' not in x]
        l = ' '.join([x.split('/')[1] for x in l if '/' in x])
        return l
    else: 
        return ''
    
df['Taxonomy'] = df['Taxonomy'].apply(taxo_strip)

#%%
def taxo_and_geo(df):
    geo = df[df.apply(lambda x: len(x['Geography']) != 0, axis=1)].copy()
    one_geo = df[df.apply(lambda x: len(x['Geography']) == 1, axis=1)].copy()
    one_geo['Geography'] = one_geo['Geography'].apply(lambda x: x[0])

    no_geo = df.drop(geo.index)
    multi_geo = geo.drop(one_geo.index)

    #
    replace_dict = {
    'United States' : ['North Carolina', 'Iowa', 'Tennessee',
        'Illinois', 'New York', 'Connecticut', 
        'Pennsylvania',
        'Massachusetts', 'Oklahoma', 
        'Colorado', 'Florida',
        'California', 
        'Texas', 'District of Columbia',
        'Nevada', 
        'Louisiana', 'Virginia', 
        'Wisconsin', 
        'Oregon', 'Kentucky', 
        'Minnesota', 'Georgia',
        'Washington', 
        'Ohio', 'New Jersey',  
        'Vermont', 
        'Maryland', 'Delaware', 
        'Utah', 
        'Nebraska', 'Kenya', 'Mexico',
        'New Hampshire', 
        'North America', 
        'Alabama', 'Silicon Valley',
        'Indiana', 
        'Alaska', 'South Carolina', 'West Virginia',
        'Michigan', 'Missouri', 'Maine', 'Rhode Island', 
        'Montana', 
        'Idaho',
        'Kansas', 
        'Arizona', 
        'Mississippi', 
        'Arkansas',
        'New Mexico'],
    'United Kingdom' : ['England',
        'Scotland',
        'Wales',
        'Northern Ireland'],
    'Canada' : ['Ontario',
        'Alberta',
        'Quebec',
        'British Columbia']
    }

    for country, sub_list in replace_dict.items():
        one_geo['Geography'] = one_geo['Geography'].apply(lambda x: country if x in sub_list else x)
        multi_geo['Geography'] = multi_geo['Geography'].apply(lambda x: country if not set(x).isdisjoint(sub_list) else x)
    rolled_up = multi_geo[multi_geo['Geography'].apply(lambda x: type(x)==str)]
    one_geo = one_geo.append(rolled_up)
    multi_geo.drop(rolled_up.index,inplace=True)

    #
    continents = [
        'Europe',
        'Latin America',
        'Asia',
        'Middle East',
        'Africa',
        'USSR',
        'West Indies', 'Caribbean',
        'Scandinavia',
        'Central America', 'South America',
        'Central & South America'
    ]

    def continent_geo(l):
        geos = [g for g in l if g not in continents]
        if len(geos) == 0:
            return l[0]
        else:
            return geos

    multi_geo['Geography'] = multi_geo['Geography'].apply(continent_geo)

    #
    remove_continent = multi_geo[multi_geo['Geography'].apply(lambda x: len(x)==1)].copy()
    remove_continent['Geography'] = remove_continent['Geography'].apply(lambda x: x[0])
    remove_continent = remove_continent.append(multi_geo[multi_geo['Geography'].apply(lambda x: type(x) == str)])

    one_geo = one_geo.append(remove_continent)
    multi_geo.drop(remove_continent.index,inplace=True)

    # 
    multi_geo['Geography'] = multi_geo['Geography'].apply(lambda x: x[0])

    one_geo = one_geo.append(multi_geo)
    all = no_geo.append(one_geo)

    if set(df['Product ID']) == set(all['Product ID']) and len(df) == len(all):
        return all
    else:
        print('something went wrong!')

df = taxo_and_geo(df)

#%%
if 'ml' not in os.listdir('/usr/local/etc/'):
    os.mkdir('/usr/local/etc/ml')
df.to_excel('/usr/local/etc/ml/processed.xlsx')

