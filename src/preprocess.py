"""Code for preprocessing dataframes for analysis."""


import utils

from collections import Counter
from generative_model import *

def create_model(wordforms, n=5, smoothing=.01):
    """Create n-gram model."""
    lm = NgramModel(n, wordforms, 1)
    lm.create_model(wordforms, smoothing)
    return lm


def obtain_length_distribution(dataframe, match_on="phones"):
    """Obtain length distribution."""
    if match_on == 'phones':
        return Counter(list(dataframe['num_phones']))
    elif match_on == 'sylls':
        return Counter(list(dataframe['num_sylls_est']))
    # Else?


def preprocess_lexicon(df, language, phon_column="PhonDISC", word_column="Word", vowels="IE{VQU@i#$u312456789cq0~",
                       n=5, smoothing=.01, match_on="phones"):
    """Preprocess Celex dataframe."""
    df['num_phones'] = df[phon_column].apply(lambda x: len(x))
    df['num_sylls_est'] = df[phon_column].apply(lambda x: utils.count_syllables(x, vowels=vowels))

    # Remove words estimates to have <1 syllables.
    df = df[df['num_sylls_est'] > 0]

    original_counts = obtain_length_distribution(df, match_on=match_on)

    ### Preprocess
    ## English
    df_processed = utils.preprocess_for_analysis(df, word_column=word_column, phon_column=phon_column).reset_index()
    unique_counts = obtain_length_distribution(df_processed, match_on=match_on)

    # Build n-gram model.
    print("Creating phonotactic model...")
    unique_wordforms = list(df_processed[phon_column])
    model = create_model(unique_wordforms, n=n, smoothing=smoothing)

    # Obtain surprisal estimates
    df_processed['log_prob'] = df_processed[phon_column].apply(lambda x: model.evaluate(x)[2])
    df_processed['surprisal'] = df_processed['log_prob'].apply(lambda x: -x)
    df['log_prob'] = df[phon_column].apply(lambda x: model.evaluate(x)[2])
    df['surprisal'] = df['log_prob'].apply(lambda x: -x)

    # Save dataframes to file
    print("Saving dataframes to file...")
    print("data/processed/{lang1}/{lang2}_celex_all.csv".format(lang1=language, lang2=language))
    df.to_csv("data/processed/{lang1}/{lang2}_all_reals.csv".format(lang1=language, lang2=language))
    df_processed.to_csv("data/processed/{lang1}/{lang2}_lemmas_processed.csv".format(lang1=language, lang2=language))

    return {'model': model,
            'original_counts': original_counts,
            'unique_counts': unique_counts,
            'original_lexicon': unique_wordforms}



