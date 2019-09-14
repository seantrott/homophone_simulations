"""Utility functions for preprocessing and analysis"""

import pandas as pd
import numpy as np 
import scipy.stats as ss

import statsmodels.formula.api as sm

import matplotlib.pyplot as plt

from tqdm import tqdm


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



######### Utils for analysis ############

def get_homophone_stats(df_lex):
    """Return basic stats about lexicon. Number of homophones, etc."""
    return {'homophone_percentage': round((len(df_lex[df_lex['num_homophones']>0]) / len(df_lex)), 4),
            'mean_homophones': round(df_lex['num_homophones'].mean(), 4),
            'max_homophones': round(df_lex['num_homophones'].max(), 2)}


def get_stats_for_lexicon(df_lex):
    """Return basic stats about lexicon. Number of homophones, etc."""
    return {'homophone_percentage': round((len(df_lex[df_lex['num_homophones']>0]) / len(df_lex)), 4),
            'mean_homophones': round(df_lex['num_homophones'].mean(), 4),
            'max_homophones': round(df_lex['num_homophones'].max(), 2),
            'mean_mp': round(df_lex['neighborhood_size'].mean(), 4),
            'max_mp': round(df_lex['neighborhood_size'].max(), 2),
            'total_mp': round(df_lex['neighborhood_size'].sum(), 2),
            'mean_mp_w_hp': round(df_lex['neighborhood_size_with_homophones'].mean(), 4),
            'max_mp_w_hp': round(df_lex['neighborhood_size_with_homophones'].max(), 2),
            'total_mp_w_hp': round(df_lex['neighborhood_size_with_homophones'].sum(), 2)}

def process_and_extract_artificials(df_artificials, N=10):
    """Extract each artificial lexicon from aggregated dataframe.
    
    Also returns information about homophony distribution and minimal pair distribution.
    """
    processed_artificials = []
    homophone_percentages = []
    mean_homophones, max_homophones = [], []
    mean_mp, max_mp, total_mp = [], [], []
    # Neighborhood size with homophones
    mean_mp_hp, max_mp_hp, total_mp_hp = [], [], []
    for i in tqdm(range(N)):

        df_tmp = df_artificials[df_artificials['lexicon']==i]

        df_tmp_processed = utils.preprocess_for_analysis(df_tmp,
                                                          phon_column="word", word_column="word")
        
        lex_stats = get_stats_for_lexicon(df_tmp_processed)

        homophone_percentages.append(lex_stats['homophone_percentage'])
        mean_homophones.append(lex_stats['mean_homophones'])
        max_homophones.append(lex_stats['max_homophones'])
        mean_mp.append(lex_stats['mean_mp'])
        max_mp.append(lex_stats['max_mp'])
        total_mp.append(lex_stats['total_mp'])
        mean_mp_hp.append(lex_stats['mean_mp_w_hp'])
        max_mp_hp.append(lex_stats['max_mp_w_hp'])
        total_mp_hp.append(lex_stats['total_mp_w_hp'])
        
        processed_artificials.append(df_tmp_processed)
    
    return {'processed_dataframes': processed_artificials,
            'homophone_percentages': homophone_percentages,
            'mean_homophones': mean_homophones,
            'max_homophones': max_homophones,
            'mean_mp': mean_mp,
            'max_mp': max_mp,
            'total_mp': total_mp,
            'mean_mp_w_hp': mean_mp_hp,
            'max_mp_w_hp': max_mp_hp,
            'total_mp_w_hp': total_mp_hp
           }
    

def plot_real_vs_art(art_dist, real_value, statistic, language, ylabel="Count"):
    """Compare distribution of test statistics from artificial lexicon to real lexicon."""
    plt.hist(art_dist)
    plt.title("{lan}: {x} (real vs. artificial)".format(lan=language, x=statistic))
    plt.xlabel(statistic)
    plt.ylabel(ylabel)
    plt.axvline(x=real_value, linestyle="dotted")


def load_lexicons_for_language(language):
    """Loads lexicons for a given language."""
    df_real = pd.read_csv("data/processed/{lan1}/minimal_pairs/{lan2}_all_mps.csv".format(lan1=language,
                                                                                         lan2=language))
    df_real_processed = utils.preprocess_for_analysis(df_real, word_column="Word", phon_column="PhonDISC")
    df_artificials = pd.read_csv("data/processed/{lan1}/minimal_pairs/{lan2}_artificial_10_matched_on_sylls_mps.csv".format(lan1=language,
                                                                                                                           lan2=language))
    return df_real, df_real_processed, df_artificials


def analyze_stats_for_single(df, formula, covariates):
    """Analyze stats for single lexicon."""
    result_real = sm.poisson(formula=formula, 
                data=df).fit(disp=0)
    
    params = result_real.params
    # params['real'] = "Yes"
    
    coefs = []
    coefs.append(params)

    return pd.DataFrame(coefs)   


def analyze_stats(df_og, list_of_artificials, formula, covariates):
    """Analyze stats for real vs artificial dataframes."""
    result_real = sm.poisson(formula=formula, 
                data=df_og).fit(disp=0)
    
    params = result_real.params
    params['real'] = "Yes"
    
    coefs = []
    coefs.append(params)
    
    for df_art in list_of_artificials:
        result_fake = sm.poisson(formula=formula, 
                data=df_art).fit(disp=0)
        params = result_fake.params
        params['real'] = "No"
        coefs.append(params)
    
    return pd.DataFrame(coefs)
    

def process_stats(df_real, list_of_fakes, formula, covariates, covariate_labels, language):
    """Pipeline for processing and plotting stats results."""
    df_stats = analyze_stats(df_real, list_of_fakes, formula=formula, covariates=covariates)
    fig = plt.figure()
    fig.set_figheight(10)
    fig.set_figwidth(10)
    for index, cov in enumerate(COVARIATES):
        ax = fig.add_subplot(len(COVARIATES), 1, index+1)

        real_value = df_stats[df_stats['real']=="Yes"][cov].values[0]
        art_values = df_stats[df_stats['real']=="No"][cov].values

        ax.hist(art_values)
        ax.axvline(x=real_value, linestyle="dotted")
        ax.axvline(x=0, linestyle="dashed")
        ax.text(s="Real coef: {sl}".format(sl=round(real_value, 2)),x=real_value, y =1)


        plt.title("{lan}: coefficient for {cov}".format(lan=LANGUAGE, cov=COVARIATE_LABELS[index]))

    fig.subplots_adjust(hspace=.5)

