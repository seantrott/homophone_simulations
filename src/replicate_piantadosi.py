"""Replicate analysis in Piantadosi et al (2012).

Specifically, ask whether #homophones correlates with:
1. Length
2. Phonotactic probability
3. Frequency

QUESTION: Do Piantadosi et al (2012) double (or triple) count homophones, or 
do they select only one of them? That is, the word "son" has at least two entries. Do they select
the frequency information from only one of these entries, or do they average it, or do they include
each as a separate observation in the model?
(It seems like including each as a separate observation overcounts.)

TO DO:
Define a few general-purpose functions:
- Identify counts for each phonological form
- Analysis (#homophones ~ Length) --> return analysis results
"""

import pandas as pd 
import scipy.stats as ss
import matplotlib.pyplot as plt


import statsmodels.formula.api as sm

import utils


# ~ 52k words, slightly different from Piantadosi
df = pd.read_csv("data/raw/celex_all.csv", sep="\\")

# Preprocess
df_processed = utils.preprocess_for_analysis(df)

# Analysis
result = sm.poisson(formula="num_homophones ~ SylCnt + CobLog", data=df_processed).fit()
result2 = sm.ols(formula="num_homophones ~ SylCnt + CobLog", data=df_processed).fit()


plt.hist(df_processed['num_homophones'])
plt.show()