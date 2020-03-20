"""Class for preprocessing lexicons."""

import pandas as pd
from collections import Counter

import src.config as config
import src.utils as utils
from src.generative_model import *



### TODO: Preprocessor should also extract/count #minimal pairs for the real lexicon and save that info.


### Utility function
def get_config_dict(config, language):

    return {'language': language,
            'phon_column': config.PHON_COLUMN[language],
            'word_column': config.WORD_COLUMN[language],
            'vowels': config.VOWEL_SETS[language],
            'match_on': config.MODEL_INFO['match_on'],
            'phonetic_remappings': config.PHONETIC_REMAPPINGS[language],
            'n': config.MODEL_INFO['n'],
            'smoothing': config.MODEL_INFO['smoothing']}


### Class for preprocessing raw data files
class Preprocessor(object):

    def __init__(self, language, phonetic_remappings, phon_column, word_column, 
                 vowels, n, smoothing, match_on):
        self.language = language
        self.df_original = self.load_original(language)
        self.phonetic_remappings = phonetic_remappings
        self.phon_column = phon_column
        self.word_column = word_column
        self.vowels = vowels
        self.n = n
        self.smoothing = smoothing
        self.match_on = match_on
        self.setup()


    def load_original(self, language):
        path, sep = config.LEXICON_PATHS[language]
        return pd.read_csv(path, sep=sep)

    def setup(self):
        if self.language in ['english', 'german']:
            self.df_preprocessed = self.df_original.copy()
            self.df_preprocessed['PhonDISC'] = self.df_preprocessed['PhonDISC'].apply(lambda x: self.remap_transcription(x))
        elif self.language in ["french"]:
            self.df_preprocessed = self.df_original[self.df_original['14_islem']==1]
        elif self.language in ['dutch']:
            self.df_preprocessed = self.df_original.dropna()
            self.df_preprocessed['PhonDISC'] = self.df_preprocessed['PhonStrsDISC'].apply(lambda x: self.remove_celex_stress(x))
            self.df_preprocessed['PhonDISC'] = self.df_preprocessed['PhonDISC'].apply(lambda x: self.remap_transcription(x))
        elif self.language in ['japanese']:
            self.df_preprocessed = self.df_original[self.df_original['morph_form']!="prop"]
            self.df_preprocessed['multiple_pronunications'] = self.df_preprocessed['phonetic_form'].apply(lambda x: "/" in x)
            self.df_preprocessed = self.df_preprocessed[self.df_preprocessed['multiple_pronunications']==False]
            self.df_preprocessed['phonetic_remapped'] = self.df_preprocessed['phonetic_form'].apply(lambda x: self.remap_transcription(x))
        elif self.language in ['mandarin']:
            print("Remapping glides")
            self.df_original['glides_remapped'] = self.df_original['IPA+T'].apply(lambda x: self.remap_glides(x))
            print("Remapping diphthongs")
            self.df_original['phonetic_remapped'] = self.df_original['glides_remapped'].apply(lambda x: self.remap_transcription(x))
            self.df_preprocessed = self.df_original.copy()

    def remove_celex_stress(self, wordform):
        """Remove stress markers to create unstressed version."""
        return wordform.replace("'", "").replace("-", "")

    def remap_transcription(self, wordform):
        """Remap any phonemes represented by double characters to single characters."""
        for og, new in self.phonetic_remappings.items():
            wordform = wordform.replace(og, new)
        return wordform

    def remap_glides(self, wordform, possible_glides=['i', 'u', 'y']):
        """Identify medial glides and remap them to the character G."""
        new_wordform = ''
        i = 0
        mandarin_vowels = self.vowels
        while i < len(wordform):
            letter = wordform[i]
            if letter in possible_glides:
                if (i+1) < len(wordform) and wordform[i+1] in mandarin_vowels:
                    new_wordform += 'G'
                    i += 1
                    continue
            
            # Otherwise, add letter
            new_wordform += letter
            i += 1
        return new_wordform

    def obtain_length_distribution(self, dataframe, match_on="phones"):
        """Obtain length distribution."""
        if match_on == 'phones':
            return Counter(list(dataframe['num_phones']))
        elif match_on == 'sylls':
            return Counter(list(dataframe['num_sylls_est']))

    def create_model(self, wordforms, n=5, smoothing=.01):
        """Create n-gram model."""
        lm = NgramModel(n, wordforms, 1)
        lm.create_model(wordforms, smoothing)
        return lm

    def preprocess_lexicon(self):
        """Preprocess Celex dataframe."""
        self.df_preprocessed['num_phones'] = self.df_preprocessed[self.phon_column].apply(lambda x: len(x))
        self.df_preprocessed['num_sylls_est'] = self.df_preprocessed[self.phon_column].apply(lambda x: utils.count_syllables(x, language=self.language, vowels=self.vowels))

        # Remove words estimates to have <1 syllables.
        self.df_preprocessed = self.df_preprocessed[self.df_preprocessed['num_sylls_est'] > 0]

        # Obtain estimate of counts for original lexicon
        original_counts = self.obtain_length_distribution(self.df_preprocessed, match_on=self.match_on)

        ### Preprocess
        self.df_processed = utils.preprocess_for_analysis(self.df_preprocessed, word_column=self.word_column, phon_column=self.phon_column).reset_index()
        unique_counts = self.obtain_length_distribution(self.df_processed, match_on=self.match_on)

        # Build n-gram model.
        print("Creating phonotactic model...")
        unique_wordforms = list(self.df_processed[self.phon_column])
        model = self.create_model(unique_wordforms, n=self.n, smoothing=self.smoothing)

        # Obtain surprisal estimates
        self.df_processed['log_prob'] = self.df_processed[self.phon_column].apply(lambda x: model.evaluate(x)[2])
        self.df_processed['surprisal'] = self.df_processed['log_prob'].apply(lambda x: -x)
        self.df_preprocessed['log_prob'] = self.df_preprocessed[self.phon_column].apply(lambda x: model.evaluate(x)[2])
        self.df_preprocessed['surprisal'] = self.df_preprocessed['log_prob'].apply(lambda x: -x)

        # Get homophone ranks
        self.df_processed['rank_num_homophones'] = self.df_processed['num_homophones'].rank(ascending=False, method="first")

        # Save dataframes to file
        print("Saving dataframes to file...")
        print("data/processed/{lang1}/{lang2}_all_reals_{n}phone.csv".format(lang1=self.language, lang2=self.language, n = self.n))
        self.df_preprocessed.to_csv("data/processed/{lang1}/{lang2}_all_reals_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))
        print("data/processed/{lang1}/{lang2}_lemmas_processed_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))
        self.df_processed.to_csv("data/processed/{lang1}/{lang2}_lemmas_processed_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))

        return {'model': model,
                'original_counts': original_counts,
                'unique_counts': unique_counts,
                'original_lexicon': unique_wordforms,
                'homophone_rank_distribution': dict(self.df_processed[['rank_num_homophones', 'num_homophones']].values)}



