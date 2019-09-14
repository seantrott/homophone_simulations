"""Generate artificial lexicon."""

import os
import pandas as pd 
from tqdm import tqdm

import utils
import config 
from preprocess import preprocess_lexicon




# match original distribution (including homophones) or distribution of unique lemma lengths?
def build_lexicon(lm, length_dist, vowels, original_lexicon, match_on='phones', lex_num=1):
    """Build a lexicon matching the distribution of lengths in length_dist.

    Parameters
    ----------
    lm: NGram
       n-gram model to evaluate/generate plausible wordforms
    length_dist: dict
       dictionary with info about number of words of each length
    lex_num: int (default 1)
        which lexicon is being built
    """
    artificial_lengths = length_dist.copy()
    new_words = []
    while True:
        w = lm.generate()[0]
        num_phones = len(w)
        num_sylls = utils.count_syllables(w, vowels=vowels)
        word_length = num_phones if match_on == "phones" else num_sylls
        if artificial_lengths[word_length] > 0:
            if w not in new_words and w not in original_lexicon:
                if any((v in vowels) for v in w):
                    artificial_lengths[word_length] -= 1
                    prob = lm.evaluate(w)[2]
                    new_words.append({
                        'word': w,
                        'num_phones': num_phones,
                        'prob': prob,
                        'num_sylls_est': num_sylls,
                        'surprisal': -prob,
                        'lexicon': lex_num})
        elif sum(artificial_lengths.values()) == 0: # 50000:
            return pd.DataFrame(new_words)


def remove_stress(wordform):
    """Remove stress markers to create unstressed version."""
    print(wordform)
    return wordform.replace("'", "").replace("-", "")

def remap_transcription(wordform):
    """Remap any phonemes represented by double characters to single characters."""
    mappings = config.PHONETIC_REMAPPINGS[config.LANGUAGE]
    for og, new in mappings.items():
        wordform = wordform.replace(og, new)
    return wordform

### Set up directories
if not os.path.exists("data/processed/{lan}".format(lan=config.LANGUAGE)):
    print("Creating directory: data/processed/{lan}".format(lan=config.LANGUAGE))
    os.mkdir("data/processed/{lan}".format(lan=config.LANGUAGE))


### Read in dataframe
path, sep = config.LEXICON_PATHS[config.LANGUAGE]
df = pd.read_csv(path, sep=sep)


### Extract params
PHON_COLUMN = config.PHON_COLUMN[config.LANGUAGE]
WORD_COLUMN = config.WORD_COLUMN[config.LANGUAGE]


if config.LANGUAGE in ['english', 'german']:
    info_for_generation = preprocess_lexicon(df, language=config.LANGUAGE, phon_column=PHON_COLUMN, word_column=WORD_COLUMN, vowels=config.VOWEL_SETS[config.LANGUAGE],
                                             **config.MODEL_INFO)
elif config.LANGUAGE in ['dutch']:
    df = df.dropna()
    df['PhonDISC'] = df['PhonStrsDISC'].apply(lambda x: remove_stress(x))
    info_for_generation = preprocess_lexicon(df, language=config.LANGUAGE, phon_column=PHON_COLUMN, word_column=WORD_COLUMN, vowels=config.VOWEL_SETS[config.LANGUAGE],
                                             **config.MODEL_INFO)
elif config.LANGUAGE in ['french']:
    # Keep only lemmas
    df = df[df['14_islem']==1]
    print(len(df))
    info_for_generation = preprocess_lexicon(df, language=config.LANGUAGE, phon_column=PHON_COLUMN, word_column=WORD_COLUMN, vowels=config.VOWEL_SETS[config.LANGUAGE],
                                             **config.MODEL_INFO)
elif config.LANGUAGE in ['japanese']:
    # TODO(seantrott): Maybe parameterize this preprocessing for Japanese?
    # Remove proper names
    df = df[df['morph_form']!="prop"]
    print(len(df))
    # Remove words with >1 pronunciation
    df['multiple_pronunications'] = df['phonetic_form'].apply(lambda x: "/" in x)
    df = df[df['multiple_pronunications']==False]
    print(len(df))
    # Now remap phonetic transcription so there's only one character per phoneme
    df['phonetic_remapped'] = df['phonetic_form'].apply(lambda x: remap_transcription(x))
    # Now process the data for the homophone analysis and artificial lexicon generation
    info_for_generation = preprocess_lexicon(df, language=config.LANGUAGE, phon_column=PHON_COLUMN, word_column=WORD_COLUMN, vowels=config.VOWEL_SETS[config.LANGUAGE],
                                             **config.MODEL_INFO)

artificial_lexicons = []
for lex in tqdm(range(config.ITERATIONS)):
    new_lex = build_lexicon(lm=info_for_generation['model'], length_dist=info_for_generation['original_counts'], 
                            vowels=config.VOWEL_SETS[config.LANGUAGE], 
                            original_lexicon=info_for_generation['original_lexicon'],
                            match_on=config.MODEL_INFO['match_on'], lex_num=lex)
    artificial_lexicons.append(new_lex)


df_artificial_lexicons = pd.concat(artificial_lexicons)
df_artificial_lexicons.to_csv("data/processed/{lang1}/{lang2}_artificial_{n}_matched_on_{match}.csv".format(
    lang1=config.LANGUAGE, lang2=config.LANGUAGE, n=str(config.ITERATIONS), match=config.MODEL_INFO['match_on']))



