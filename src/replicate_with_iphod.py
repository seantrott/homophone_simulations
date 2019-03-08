"""Learn phonotactics.

Important columns:
- Word: orthographic form
- UnTrn: unstressed transcription (phonemes separated by periods, e.g. ".")
- StTrn: stressed description (0, 1, 2 indicates unstressed, primary, or secondary stressed syllable)
- NSyll: #syllables
- NPhon: #phonemes
- SFreq: SUBLTEXus word frequency
- unsTPAV: unstressed word-average tri-phoneme probability
- strTPAV: stressed word-average tri-phoneme probability

Link: http://www.iphod.com/details/

"""

import pandas as pd 
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt

import utils


# Parameters
params = {'syllable_term': 'NSyll',
		  'phoneme_term': 'NPhon'}

FORMULA = 'num_homophones ~ {syl} + {prob}'.format(syl=params['syllable_term'],
												   prob='surprisal')
PHON_COLUMN = 'StTrn'

# Read in data
df = pd.read_csv("data/raw/IPhODv2.0_REALS/IPhOD2_Words.txt", sep="\t")

# Preprocess
df_processed = utils.preprocess_for_analysis(df, phon_column=PHON_COLUMN)


# Analysis
df_processed['surprisal'] = df_processed['strTPAV'] / df_processed['NPhon']
result = sm.poisson(formula=FORMULA, data=df_processed).fit()
print(result.params)



