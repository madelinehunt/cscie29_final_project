#%% 
import pandas as pd
import os
import sys
#%%
from pim.pimdata import *
a = PimData()
products = a.products

#%%
if __name__ == '__main__':
    import sys
    features = [x.strip().lower() for x in sys.argv[1].split(',')]
else:
    features = [x.strip().lower() for x in input('which features to audit?').split(',')]

print('processing: \n', features) 

#%%
df = pd.read_excel('/usr/local/etc/ml/processed.xlsx').fillna('')
mask = products[products['Product ID'].isin(df['Product ID'])].copy()
#%%
def sampler(df,col,n):
    df = df[df[col] != '']
    ret = pd.DataFrame()
    uniques = len(df[col].unique())
    groups = round(n/uniques)
    
    if groups < 10:
        counts = pd.DataFrame(df[col].value_counts()).reset_index()
        smalls = counts[counts[col] < (n*.2)]
        
        bigs = df.drop(df[df[col].isin(smalls['index'])].index)
        groups = round(n/len(bigs[col].unique())*.6)

    for u in df[col].unique():
        tmp = df[df[col] == u]
        if len(tmp) > groups:
            ret = ret.append(tmp.sample(n=groups,random_state=42))
        else:
            ret.append(tmp)
    return ret.drop_duplicates().copy()


#%%
def printer(label,string):
    return label + ':\n' + string + '\n'

def paragrapher(s):
    sentences = pd.Series(s.split('.'))
    tabs = sentences[sentences.index%5==0]
    sentences.loc[tabs.index] = tabs.apply(lambda x: str('\n\t' + x))
    return ' '.join(sentences)

#%%
def audit(whole_df,sample_df,label,nrows):
    non_audited = whole_df.drop(sample_df.index)
    working_df = sample_df.copy()
        
    cached = cache_check(label)
    if cached:
        already_done = sample_df.copy()[:len(cached)]
        already_done[label] = cached
        working_df = working_df.drop(already_done.index).copy()
    else:
        already_done = False
    if nrows:
        working_df = working_df.iloc[:nrows]
            
    if '{}_cache.txt'.format(label) not in os.listdir('/usr/local/etc/ml/audited/'):
        cache = open('/usr/local/etc/ml/audited/{}_cache.txt'.format(label),'w+').close()
    cache = open('/usr/local/etc/ml/audited/{}_cache.txt'.format(label),'a')
    for index, value in working_df.iterrows():
        os.system(r"printf '\033[2J'")
        print('------------------------------------------------------------')
        print(printer('Title',mask.iloc[index]['Title']))
        for col in [c for c in whole_df.columns if c != label and c != 'Full Text' and 'Contributor' not in c]:
            if col == 'Full Abstract':
                print(printer(col,paragrapher(value[col])))
            else:
                print(printer(col,value[col]))
        print('\t\t{}:\n'.format(label),'\t\t'+value[label],'\n')
        if needs_replacing(label) == True:
            os.system(r"printf '\033[2J'")
            if label == 'Geography':
                options_list = [x for x in list(whole_df[label].unique()) if x != '']; options_list.sort()
                full_list = a.taxonomy['Term'].unique()
            elif label == 'Major Discipline':
                options_list = [x for x in list(whole_df[label].unique()) if x != '']; options_list.sort()
                full_list = a.products['Major Discipline'].unique()
            [print(x) for x in options_list]
            print('----------------------')
            correction = 'fake'
            while correction not in full_list:
                correction = input('Which of these terms should it be?\n>')
            cache.write(correction+'\n')
            working_df.loc[index][label] = correction
        else:
            cache.write(value[label]+'\n')
    os.system(r"printf '\033[2J'")
    print('All done!\nExporting…')
    if type(already_done) == pd.core.frame.DataFrame:
        working_df = already_done.append(working_df)
    if nrows:
        working_df.to_excel('/usr/local/etc/ml/audited/{}_audited.xlsx'.format(label))
    else:
        working_df.to_excel('/usr/local/etc/ml/audited/{}_audited.xlsx'.format(label))
        non_audited.to_excel('/usr/local/etc/ml/audited/{}_not_audited.xlsx'.format(label))
    cache.close()
    # return working_df

def needs_replacing(label):
    check = ''
    while len(check) < 1:
        check = input('Is the {} correct?\n>'.format(label)).lower()
    if check != 'y' and check != 'yes' and check[0] != 'y':
        return True
    else:
        return False
#%% 
def cache_check(label):
    if '{}_cache.txt'.format(label) in os.listdir('/usr/local/etc/ml/audited/'):
        lines = []
        with open('/usr/local/etc/ml/audited/{}_cache.txt'.format(label)) as f:
            for line in f.readlines():
                if line != '' and line != '\n':
                    lines.append(line)
        f.close()
        return lines
    else:
        return False
            

#%%
if len(sys.argv) > 2:
    try:
        nrows = int(sys.argv[2].strip())
    except:
        print('something went wrong with nrows… have you tried passing in a number?\n\n')
else:
    nrows = False


#%%
if 'audited' not in os.listdir('/usr/local/etc/ml'):
    os.mkdir('/usr/local/etc/ml/audited')

#%%
if 'geography' in features:
    geo_X = sampler(df,'Geography',200)
    audit(df,geo_X,'Geography',nrows)
if 'discipline' in features or 'disc' in features or 'maj_disc' in features:
    maj_disc_X = sampler(df,'Major Discipline',200)
    audit(df,maj_disc_X,'Major Discipline',nrows)


#%%
# head = products.head(n=10)
# a = [2,4,1,1]
# b = head[:len(a)].copy()
# b['Product ID'] = a
# b