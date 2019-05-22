"""Utility functions for preprocessing and analysis"""

import pandas as pd
import numpy as np 
import scipy.stats as ss


def get_homophone_counts(df, column="PhonDISC"):
    """Return a Series mapping each form to the number of occurrences.
    Use stressed or unstressed?
    """
    return df.groupby(column).size() - 1


def remove_word(word):
    """Tag word for removal."""
    return " " in word or "-" in word or "'" in word


def preprocess_for_analysis(df, word_column="Word", phon_column='PhonDISC', verbose=False):
    """Preprocess dataframe."""
    df = df.dropna(subset=[word_column])
    if verbose:
        print("Number of tokens: {t}".format(t = len(df)))

    # Remove words according to Piantadosi
    # (From original paper) We excluded words in CELEX containing spaces, hyphens, or apostrophes, 
    # leaving 65,417 English phonological forms, 310,668 German phonological forms, 
    # and 277,522 Dutch phonological forms.
    df['remove'] = df[word_column].apply(remove_word)
    df = df[df['remove'] == False]
    if verbose:
        print("Number of tokens: {t}".format(t = len(df)))

    # Get number of homophones
    phone_counts = get_homophone_counts(df, column=phon_column)
    # Merge together
    df['num_homophones'] = df[phon_column].apply(lambda x: phone_counts[x])

    # Remove duplicates now? *** Should this be allowed? If so, how to decide which duplicate to drop?
    # (Depends on what their procedure was)
    df = df.drop_duplicates(subset=phon_column)
    if verbose:
        print("Number of tokens: {t}".format(t = len(df)))

    return df

def agg_homophones_by_syllable(dataframe, syl_column = "NSyll", homophone_column='num_homophones'):
    """Aggregate homophones by number of syllables."""
    means_table = pd.pivot_table(dataframe, values=homophone_column,
               columns=syl_column,
               aggfunc=np.mean)
    sem_table = pd.pivot_table(dataframe, values=homophone_column,
                   columns=syl_column,
                   aggfunc=ss.sem)
    
    num_sylls = list(set(list(dataframe[syl_column])))
    means = [means_table[i][homophone_column] if i in means_table else 0 for i in num_sylls]
    sems = [1*sem_table[i][homophone_column] if i in sem_table else 0 for i in num_sylls]
    
    return pd.DataFrame.from_dict({'num_sylls': num_sylls,
                                   'mean_homophones': means,
                                   'sem_homophones': sems})


def get_number_and_percent_homophones(dataframe, homophone_column='num_homophones'):
    """Get number and percentage of homophonous wordforms."""
    X = len(dataframe[dataframe[homophone_column]>=1])
    X_per = round((X / len(dataframe)) * 100, 2)
    return [X, X_per]


def count_syllables(word, vowels="IE{VQU@i#$u312456789cq0~"):
    """Counts number of vowels in word for rough estimate of number of syllables.
    Use: http://groups.linguistics.northwestern.edu/speech_comm_group/documents/CELEX/Phonetic%20codes%20for%20CELEX.pdf
    
    Change vowels based on language.
    """
    counts = 0
    for i in word:
        if i in vowels:
            counts += 1
    return counts


