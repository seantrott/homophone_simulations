"""Code to simulate sound changes in lexicons."""

import pandas as pd 
from tqdm import tqdm 

import utils
import config 
import preprocess


def implement_unconditioned_sound_change(wordforms, rule):
    """Implement sound change across a lexicon of phonological wordforms.
    
    Parameters
    ----------
    wordforms: list
       list of strings representing phonological wordforms
    rule: tuple
       tuple with first element representing original sound, second 
       representing new sound
    """
    new_wordforms = [word.replace(rule[0], rule[1]) for word in wordforms]
    return new_wordforms


def apply_sound_change(df, rule, phon_column="PhonDISC"):
    """Apply sound change and recalculate stats."""
    df_copy = df.copy()
    df_copy['new_lexicon'] = implement_unconditioned_sound_change(list(df_copy[phon_column]), rule)

    # Reprocess
    df_copy_processed = utils.preprocess_for_analysis(df_copy, phon_column='new_lexicon', word_column="new_lexicon")
    new_lexicon_stats = utils.get_homophone_stats(df_copy_processed)

    # Recalculate surprisal for changed words
    df_copy_processed['surprisal'] = df_copy_processed['new_lexicon'].apply(lambda x: -MODEL.evaluate(x)[2])

    # Rerun stats for new lexicon.
    model_stats = utils.analyze_stats_for_single(df_copy_processed, formula=FORMULA, covariates=COVARIATES)
    
    # Return changed lexicon, descriptive stats, and new model stats
    return df_copy, new_lexicon_stats, model_stats


def apply_individually_to_lexicon(df_lexicon, rules, index = "real"):
    """Apply each sound change to a given lexicon, return resulting statistics."""
    descriptive_stats = []
    model_stats = []

    phon_column = "PhonDISC" if index == "real" else "word"
    word_column = "Word" if index == "real" else "word"

    baseline_processed = utils.preprocess_for_analysis(df_lexicon, phon_column=phon_column, 
                word_column=word_column)
    baseline_model = utils.analyze_stats_for_single(baseline_processed, formula=FORMULA, covariates=COVARIATES)
    og_coef = baseline_model['num_sylls_est'].values[0]

    for rule in tqdm(rules):
        str_rule = "{x1} --> {x2}".format(x1=rule[0], x2=rule[1])
        df_morphed, lex_stats, m_stats = apply_sound_change(df_lexicon, rule, phon_column=phon_column)
       
        lex_stats['n'] = index
        lex_stats['rule'] = str_rule
        
        m_stats['n'] = index
        m_stats['rule'] = str_rule
        m_stats['diff'] = m_stats['num_sylls_est'].values[0] - og_coef
        
        descriptive_stats.append(lex_stats)
        model_stats.append(m_stats)

    return df_morphed, descriptive_stats, model_stats


def apply_serially_to_lexicon(lexicon, rules):
    """Apply sound changes serially.

    Here, it'd be nice to collect "diff" at each stage. So we can know whether sound changes
    made at stage 1 are systematically different than stage 5, or whether they're just additive.
    """
    pass 


def apply_individually_to_lexicons(lexicons, rules):
    """Apply each sound change to each lexicon in turn."""
    descriptive_stats_art, model_stats_art = [], []
    for index, baseline in enumerate(lexicons):
        
        _, ds, ms = apply_individually_to_lexicon(baseline, rules, index=index)
    return descriptive_stats_art, model_stats_art


FORMULA = "num_homophones ~ surprisal + num_sylls_est"
COVARIATES = ['surprisal', 'num_sylls_est']


grimms_law = [('b', 'p'),
              ('d', 't'),
             ('g', 'k'),
             ('p', 'f'),
             ('t', 'T'),
             ('k', 'h')]


great_vowel_shift = [ ('i', '2') ,
                    ('3', 'i'),
                     ('#', '1'),
                    ('u', '5') ,
                     ('$', '5')]

all_rules = grimms_law + great_vowel_shift



df_real = pd.read_csv("data/processed/english/english_all_reals.csv")

MODEL = preprocess.create_model(df_real['PhonDISC'])


ds, ms = apply_individually_to_lexicon(df_real, all_rules)

