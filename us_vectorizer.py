import pandas as pd
import numpy as np
import os

from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

#%%
def vectorize_and_pca(series):
    tf = TfidfVectorizer()
    t = tf.fit_transform(series)
    pca = PCA(360)
    p = pca.fit_transform(t.toarray())
    return p

#%%
us_corrected = pd.read_excel('/usr/local/etc/ml/audited/final/us_audited.xlsx').fillna('')
# us_non_audited = pd.read_excel('/usr/local/etc/ml/audited/final/us_not_audited_final.xlsx').fillna('')

#%%
us_corrected_X
#%%
us_corrected_X = vectorize_and_pca(us_corrected['Full Text'])

#%%
us_non_audited_X = vectorize_and_pca(us_non_audited['Full Text'])

#%%
us_to_cache = pd.DataFrame(us_corrected_X)
us_to_cache
#%%
us_n_to_cache = pd.DataFrame(us_non_audited_X)

#%%
if 'cached_us' not in os.listdir('/usr/local/etc/ml/'):
    os.mkdir('/usr/local/etc/ml/cached_us')

#%%

us_to_cache.to_excel('/usr/local/etc/ml/cached_us/us_audited_final.xlsx')
us_n_to_cache.to_excel('/usr/local/etc/ml/cached_us/us_not_audited_final.xlsx')