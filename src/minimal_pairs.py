"""Code to identify number of minimal pairs for each word in a lexicon."""

import os
import os.path as op
import pandas as pd 
import itertools
import math

import editdistance as ed

from collections import defaultdict
from tqdm import tqdm

import src.config as config
import src.utils as utils

import re


def generate_mp_regex(wordform):
    regex = "^("
    forms = []
    # mutations
    for index in range(len(wordform)):
        forms.append(wordform[:index] + '.' + wordform[index+1:])

    # insertions
    for index in range(len(wordform) + 1):
        forms.append(wordform[:index] + '.' + wordform[index:])

    # deletions
    for index in range(len(wordform)):
        forms.append(wordform[:index] + wordform[index+1:])
    regex += "|".join(forms)

    regex = regex.replace("$", "\$")
    regex += ")$"
    return regex

def find_minimal_pairs_lazy(wordforms):
    word_to_size = defaultdict(int)
    # unique_combos = math.factorial(len(wordforms)) / (math.factorial(2) * (math.factorial(len(wordforms)-2)))
    seen = set()
    for w1 in tqdm(wordforms):
        seen.add(w1)
        regex = re.compile(generate_mp_regex(w1))
        matches = [w for w in wordforms if w not in seen and regex.match(w)]
        for w2 in matches:
            word_to_size[w1] += 1
            word_to_size[w2] += 1
    return word_to_size


def find_minimal_pairs(wordforms, counts):
    """For each word, find number of minimal pairs."""
    word_to_size = defaultdict(int)
    word_to_size_with_homophones = defaultdict(int)
    unique_combos = math.factorial(len(wordforms)) / (math.factorial(2) * (math.factorial(len(wordforms)-2)))
    seen = []
    with tqdm(total=unique_combos) as progress_bar:
        for w1, w2 in itertools.combinations(wordforms, 2):
            # "Minimal pair" is defined here as wordforms 1 distance away. .
            if ed.eval(w1, w2) == 1:
                word_to_size[w1] += 1
                word_to_size[w2] += 1
                word_to_size_with_homophones[w1] += counts[w2] + 1
                word_to_size_with_homophones[w2] += counts[w1] + 1
            progress_bar.update(1)

    return word_to_size, word_to_size_with_homophones


def mps_for_lexicon(df_lex, phon_column="PhonDISC", unique=True):
    """Get minimal pairs for each word, put into lexicon."""
    df_lex = df_lex.dropna(subset=[phon_column])

    # Get homophone counts
    homophone_counts = utils.get_homophone_counts(df_lex, column=phon_column)

    # Get unique wordforms
    wordforms = df_lex[phon_column].values
    wordforms = set(wordforms)

    # Print out num wordforms
    num_wordforms = len(wordforms)
    print("#words: {l}".format(l=num_wordforms))

    # Get num of minimal pairs
    neighborhood_size, neighborhood_size_with_homophones = find_minimal_pairs(wordforms, counts=homophone_counts)
    df_lex['neighborhood_size'] = df_lex[phon_column].apply(lambda x: neighborhood_size[x])
    df_lex['neighborhood_size_with_homophones'] = df_lex[phon_column].apply(lambda x: neighborhood_size_with_homophones[x])
    return df_lex



def mps_for_artificials(df_arts, N):
    """For each artificial lexicon, get minimal pairs for each word."""
    artificials = []
    for lex in range(N):
        df_lex = df_arts[df_arts['lexicon']==lex]
        df_lex = mps_for_lexicon(df_lex, phon_column='word')
        artificials.append(df_lex)
    df_all_arts = pd.concat(artificials)
    
    return df_all_arts


def main(language, N, matched, mp_dir, phon_column="PhonDISC", 
         nphones=5, anti_homophony=True):
    """Main script."""

    ## Load files
    dir_path = "data/processed/{lan}".format(lan=language)
    art_string = "{lan}_artificial_{N}_matched_on_{match}_no_restriction_{n}phone_selection_{anti}.csv".format(lan=language, N=N, match=matched, n=nphones, anti=anti_homophony)
    artificial_path = op.join(dir_path, art_string)

    print(artificial_path)

    # Load lexicons
    df_real = pd.read_csv(op.join(dir_path, "{lan}_all_reals_{n}phone.csv".format(lan=language, n=nphones)))
    df_artificials = pd.read_csv(artificial_path)

    # Get minimal pairs for real lexicon
    print("Getting minimal pairs for real lexicon...")
    df_real_mps = mps_for_lexicon(df_real, phon_column=phon_column)
    df_real_mps.to_csv("{dir}/{lan}_all_mps_{n}phone.csv".format(dir=mp_dir, lan=language, n=nphones))

    # Get minimal pairs for artificials
    print("Getting minimal pairs for artificial lexicons...")
    df_arts_mps = mps_for_artificials(df_artificials, N=N)
    df_arts_mps.to_csv("{dir}/{f}".format(dir=mp_dir, f=art_string.replace("sylls", "sylls_mps")))





if __name__ == "__main__":
    # Get params
    language = config.LANGUAGE
    N = config.ITERATIONS
    matched = config.MODEL_INFO['match_on']
    phon_column = config.PHON_COLUMN[language]
    nphones = config.MODEL_INFO['n']
    anti_homophony = config.SELECTION_PARAMETERS['select_against_homophones']

    ## Check for directories
    mp_dir = "data/processed/{lan}/minimal_pairs".format(lan=config.LANGUAGE)
    if not os.path.exists(mp_dir):
        print("Creating directory: {dir}".format(dir=mp_dir))
        os.mkdir(mp_dir)

    # Run main script
    main(language=language, N=N, matched=matched, mp_dir=mp_dir, phon_column=phon_column, 
         nphones=nphones, anti_homophony=anti_homophony)






