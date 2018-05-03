from pim.pimdata import *
import os
a = PimData()
products = a.products
import re

#%% filter based on Copyright Holder
hs = [x for x in list(products['Copyright Holder'].unique()) if 'Harvard' in x or 'HBS' in x or 'HBP' in x or 'HBSP' in x]
hs = [x for x in hs if x != 'Non-HBS']

#%%
he = products[
    (products['Business Group'] == 'Higher Education') &
    (products['Status'].isin(['P','S','T']) == False) &
    (products['Availability Product State'] == 'Approved (All)') &
    (products['Language'] == 'ENG') &
    (products['Copyright Holder'].isin(hs))
]

he = he.drop_duplicates(subset='Availability Part Number')

#%% get list of all products
def get_files(dir):
    files_list = []
    for file_tuple in os.walk(dir):
        files = file_tuple[2]
        if len(files) > 0:
            files_list += files
    return files_list

pdf_files = get_files('/Users/nathaniel.hunt/Desktop/pdf downloads/')    
epub_files = get_files('/Users/nathaniel.hunt/Desktop/epub downloads/')    

def extract_avails(file_list):
    file_types = ['c2','p2','t2','f2','s2','f1','w2']
    ret_list = []
    for t in file_types:
        for f in file_list:
            if t in f:
                ret_f = f.split(t)[0]
                ret_list.append(ret_f)
            elif '.epub' in f:
                ret_f = f.split('.')[0]
                ret_list.append(ret_f)
    return pd.Series(ret_list).drop_duplicates()

pdfs = extract_avails(pdf_files)
epubs = extract_avails(epub_files)

both = pdfs.append(epubs)

#%%
def key_strip(fname):
    file_types = ['c2','p2','t2','f2','s2','f1','w2']
    if '.DS' not in fname:
        for t in file_types:
            if t in fname:
                k = fname.split(t)[0]
                return k

def get_files_dict(dir):
    files_dict = {}
    for file_tuple in os.walk(dir):
        files = file_tuple[2]
        branch = file_tuple[0]
        if len(files) > 0:
            for f in files:
                if 'pdf' in dir:
                    k = key_strip(f)
                else:
                    k = f.split('.')[0]
                if k not in files_dict.keys():
                    files_dict[k] = str(branch+'/'+f)
    return files_dict

pdf_dict = get_files_dict('/Users/nathaniel.hunt/Desktop/pdf converted/')
epub_dict = get_files_dict('/Users/nathaniel.hunt/Desktop/epub converted/')

#%% prepare DF for text import
df = he[he['Availability Part Number'].isin(both)]
df = df[['Availability Part Number']].rename(columns={'Availability Part Number':'Product ID'})
df['PDF Filepath'] = df['Product ID'].map(pdf_dict)
df['EPUB Filepath'] = df['Product ID'].map(epub_dict)
df.fillna('',inplace=True)
df['PDF Text'] = ''
df['EPUB Text'] = ''
#%%
def read_text(fpath,encoding):
    if fpath != '':
        fs = open(fpath, 'r+', encoding = encoding)
        txt = fs.read()
        txt = re.sub('\n', ' ',txt)
        return txt

df['PDF Text'] = df['PDF Filepath'].apply(read_text,args=('macintosh',))
df['EPUB Text'] = df['EPUB Filepath'].apply(read_text,args=('utf8',))
df.fillna('',inplace=True)

#%% caching my df (outputs a 268 MB xlsx)
if 'nltk' not in os.listdir('/usr/local/etc/'):
    os.mkdir('/usr/local/etc/nltk')
df.to_excel('/usr/local/etc/nltk/df.xlsx')
