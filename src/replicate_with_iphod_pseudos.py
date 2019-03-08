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


TO DO:
- Sample N with frequency/length/phonotactic characteristics from true IPHOD
- Do we use stressed vs. unstressed?
- Can we just use tri-phoneme probability as metric for phonotactic surprisal?

"""

import pandas as pd 
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt

from os import listdir
from tqdm import tqdm

import utils

# Parameters
# Parameters
params = {'syllable_term': 'NSyll',
		  'phoneme_term': 'NPhon'}

FORMULA = 'num_homophones ~ {syl} + {prob}'.format(syl=params['syllable_term'],
												   prob='surprisal')
PHON_COLUMN = 'StTrn'
PATH = "data/raw/IPhODv2.0_PSEUDO"

# Number of words to sample
N = 50000
# Number of draws from lexicon
ITERATIONS = 100
# Previous result on real data
REAL_SLOPE = -1.039393 # a-.03 for OLS regression, -1.039393 for Poisson
REAL_PHONOTACTIC_SLOPE = 83.110092  # e.g. for surprisal term

# Read in data
sources = []
files = listdir(PATH)
print("Loading pseudo-words from files...")
for f in tqdm(files):
	if "IPhOD2_Pseudos" in f:
		temp = pd.read_csv("{path}/{file_name}".format(path=PATH, file_name=f), sep="\t")
		sources.append(temp)

df = pd.concat(sources)


# Remove any heterographic homophones
# df_homophones = utils.get_homophone_counts(df, column="StTrn")
df = df.drop_duplicates(subset=PHON_COLUMN)



"""
Maybe, to get a distribution approximating the length/frequency of English words,
we get a set of proportions (or counts) corresponding to possible syllable lengths, e.g.:
{2: 21402, 3: 14433, 1: 8428, 4: 6804, 5: 2408, 6: 485, 7: 56, 8: 8, 0: 3, 12: 1, 9: 1}
We then use these proportions to determine how many of each syllable to sample from in our pseudowords:

"""
test = {2: 21402, 3: 14433, 1: 8428, 4: 6804, 5: 2408, 6: 485, 7: 56, 8: 8, 12: 1, 9: 1}

length_coefs, phonotactic_coefs = [], []

df['surprisal'] = df['strTPAV'] / df['NPhon']
for i in tqdm(list(range(ITERATIONS))):

	# Sample an appropriate amount of words from each length
	temp = []
	for syl, num in test.items():
		df_subset = df[df['NSyll']==syl]
		if len(df_subset) > 0: # num
			temp.append(df_subset.sample(num, 
										 replace=True,
										 weights=df_subset['surprisal']))

	
	df_sampled = pd.concat(temp)

	# df_sampled = df.sample(N, replace=True)
	df_sampled['Word_recoded'] = df_sampled['Word'].apply(lambda x: x.split(" (")[0])

	# Preprocess
	df_processed = utils.preprocess_for_analysis(df_sampled, 
												 word_column='Word_recoded',
												 phon_column=PHON_COLUMN)

	# df_processed.hist('NSyll')
	# plt.show()

	# Analysis
	result = sm.poisson(formula=FORMULA, data=df_processed).fit()

	length_coefs.append(result.params['NSyll'])
	phonotactic_coefs.append(result.params['surprisal'])



mean_random_slope = sum(length_coefs)/len(length_coefs)

plt.hist(length_coefs)
plt.axvline(x=REAL_SLOPE, linestyle="dotted")
plt.axvline(x=mean_random_slope, linestyle="dotted", color="blue")
#plt.text(s="Real slope: {sl}".format(sl=REAL_SLOPE),x=REAL_SLOPE, y=5)
# plt.xlim(-.05, .05)
plt.show()


plt.hist(phonotactic_coefs)
plt.axvline(x=REAL_PHONOTACTIC_SLOPE, linestyle="dotted")
# plt.axvline(x=mean_random_slope, linestyle="dotted", color="blue")
plt.text(s="Real slope: {sl}".format(sl=REAL_PHONOTACTIC_SLOPE),
		 x=REAL_PHONOTACTIC_SLOPE, y=5)
plt.show()

