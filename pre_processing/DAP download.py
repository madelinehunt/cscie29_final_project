from pim.pimdata import *
a = PimData()
products = a.products

#%%
he = products[
    ((products['Business Group'] == 'Higher Education') | (products['HE Eligible'] == 'Y')) &
    (products['Status'].isin(['P','S','T']) == False) &
    (products['Core Product State'] == 'Approved (All)')
]

#%%
prods = he['Availability Part Number'].values
prods

#%% SFTP connection to DAP
import pysftp
import pandas as pd
import os

#%% 
srv = pysftp.Connection(host="xxxxxxxxx", username="xxxxxxxx",
password='xxxxxx')


#%%
dap_files = open('/Users/nathaniel.hunt/Desktop/files.txt','r')
all_lines = []
for line in dap_files.readlines():
    all_lines.append(line.strip('\n'))

file_types = ['c2','p2','t2','f2','s2','f1','w2']

files_dict = {}
for l in all_lines:
    avail = l.split('/')[-1]
    for t in file_types:
        if t in avail:
            avail = avail.split(t)[0]
            files_dict[l] = avail
        elif 'epub' in avail:
            avail = avail.split('.')[0]
            files_dict[l] = avail
t = pd.DataFrame(data=pd.Series(files_dict))
t.rename(columns = {0: 'Avail'}, inplace=True)
t['Filepath'] = t.index
t = t.reset_index()
t = t.drop('index',axis=1)
len(t[~t['Avail'].isin(prods)])


pdfs = t[t['Filepath'].str.contains('pdf')]
epubs = t[t['Filepath'].str.contains('epub')]


len(pdfs)
len(epubs)



#%% 
testing = pdfs.sample(n=100)
#%%
os.chdir('/Users/nathaniel.hunt/Desktop/')
if 'pdf downloads' not in os.listdir('/Users/nathaniel.hunt/Desktop/'):
    os.mkdir('pdf downloads')

if 'epub downloads' not in os.listdir('/Users/nathaniel.hunt/Desktop'):
    os.mkdir('epub downloads')

def pdf_downloader(row,t):
    filepath = row['Filepath']
    fname = filepath.split('/')[-1]
    lcd = '/Users/nathaniel.hunt/Desktop/pdf downloads/'+str(t)+'/'
    srv.get(filepath,localpath=lcd+fname)

def epub_downloader(row,t):
    filepath = row['Filepath']
    fname = filepath.split('/')[-1]
    lcd = '/Users/nathaniel.hunt/Desktop/epub downloads/'+str(t)+'/'
    srv.get(filepath,localpath=lcd+fname)

#%% batching
import numpy as np

def batch_maker(df):
    pairs = []
    ranges = np.linspace(0,len(df),dtype=int)
    for n in range(len(ranges)):
        try:
            n1 = n + 1
            t = (ranges[n],ranges[n1])
            pairs.append(t)
        except:
            pass
    return pairs
    
pdf_pairs = batch_maker(pdfs)
epub_pairs = batch_maker(epubs)
        
#%% batch downloading

#%%
def batching_pdfs(t):
    if str(t) not in os.listdir('/Users/nathaniel.hunt/Desktop/pdf downloads/'):
        lcd = '/Users/nathaniel.hunt/Desktop/pdf downloads/'+str(t)+'/'
        os.mkdir(lcd)
        tmp = pdfs[t[0]:t[1]]
        tmp.apply(pdf_downloader,axis=1,args=(t,))
        
        
def batching_epubs(t):
    if str(t) not in os.listdir('/Users/nathaniel.hunt/Desktop/epub downloads/'):
        lcd = '/Users/nathaniel.hunt/Desktop/epub downloads/'+str(t)+'/'
        os.mkdir(lcd)
        tmp = epubs[t[0]:t[1]]
        tmp.apply(epub_downloader,axis=1,args=(t,))

for li in pdf_pairs:
    batching_pdfs(li)
    
for li in epub_pairs:
    batching_epubs(li)