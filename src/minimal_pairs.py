"""Code to identify number of minimal pairs for each word in a lexicon."""

import os
import os.path as op
import pandas as pd 
import itertools

import editdistance as ed

from collections import defaultdict
from tqdm import tqdm

import config 
import utils



def find_minimal_pairs(wordforms):
	"""For each word, find number of minimal pairs."""
	word_to_size = defaultdict(int)
	for w1, w2 in itertools.combinations(wordforms, 2):
		if ed.eval(w1, w2) == 1:
			word_to_size[w1] += 1
			word_to_size[w2] += 1

	return word_to_size


def mps_for_lexicon(df_lex, phon_column="PhonDISC"):
	"""Get minimal pairs for each word, put into lexicon."""
	wordforms = df_lex[phon_column].values
	num_wordforms = len(wordforms)
	print("#words: {l}".format(l=num_wordforms))
	# print('#Combinations: ')
	neighborhood_size = find_minimal_pairs(wordforms)
	df_lex['neighborhood_size'] = df_lex[phon_column].apply(lambda x: neighborhood_size[x])
	return df_lex


def mps_for_artificials(df_arts, N):
	"""For each artificial lexicon, get minimal pairs for each word."""
	artificials = []
	for lex in range(N):
		df_lex = df_arts[df_arts['lexicon']==lex]
		df_lex = mps_for_lexicon(df_lex_processed, 'word')
		artificials.append(df_lex)
	df_all_arts = pd.concat(artificials)
	# 
	return df_all_arts


def main(language, N, matched, mp_dir):
	"""Main script."""

	## Load files
	dir_path = "data/processed/{lan}".format(lan=language)
	art_string = "{lan}_artificial_{N}_matched_on_{match}.csv".format(lan=language, N=N, match=matched)
	artificial_path = op.join(dir_path, art_string)

	# Load lexicons
	df_real = pd.read_csv(op.join(dir_path, "{lan}_all_reals.csv".format(lan=language)))
	df_artificials = pd.read_csv(artificial_path)

	# Get minimal pairs for real lexicon
	print("Getting minimal pairs for real lexicon...")
	df_real_mps = mps_for_lexicon(df_real, phon_column="PhonDISC")
	df_real_mps.to_csv("{dir}/{lan}_all_mps.csv".format(dir=mp_dir, lan=language))

	# Get minimal pairs for artificials
	print("Getting minimal pairs for artificial lexicons...")
	df_arts_mps = mps_for_artificials(df_artificials, N=N)
	df_arts_mps.to_csv("{dir}/{f}".format(dir=mp_dir, f=art_string.replace("sylls", "sylls_mps")))





if __name__ == "__main__":
	# Get params
	language = config.LANGUAGE
	N = config.ITERATIONS
	matched = config.MODEL_INFO['match_on']

	## Check for directories
	mp_dir = "data/processed/{lan}/minimal_pairs".format(lan=config.LANGUAGE)
	if not os.path.exists(mp_dir):
	    print("Creating directory: {dir}".format(dir=mp_dir))
	    os.mkdir(mp_dir)

	# Run main script
	main(language=language, N=N, matched=matched, mp_dir=mp_dir)






