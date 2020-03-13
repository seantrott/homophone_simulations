"""Main functions."""


import argparse
import os
import pandas as pd

import src.config as config

from src.analysis import Analyzer, get_analysis_parameters
from src.lexicon_builder import LexiconBuilder
from src.preprocessor import Preprocessor, get_config_dict


LANGUAGES = ['german', 'dutch', 'japanese', 'french', 'mandarin']

# LANGUAGES = ['japanese', 'french', 'mandarin']


def preprocess_lexicon(language):
    """Preprocess lexicon."""
    config_dict = get_config_dict(config, language)
    preprocessor = Preprocessor(**config_dict)
    preprocessor.setup()
    info_for_generation = preprocessor.preprocess_lexicon()
    return info_for_generation



def generate_lexica():
    """Generate lexica for each language."""

    ## TODO: Run in each mode: ['neutral', 'anti_homophones', 'pro_neighborhoods']
    
    for language in LANGUAGES:
        ### Set up directories
        print("Building lexica for: {language}".format(language=language))
        if not os.path.exists("data/processed/{lan}".format(lan=language)):
            print("Creating directory: data/processed/{lan}".format(lan=language))
            os.mkdir("data/processed/{lan}".format(lan=language))
        if not os.path.exists("data/processed/{lan}/artificials".format(lan=language)):
            print("Creating directory: data/processed/{lan}/artificials".format(lan=language))
            os.mkdir("data/processed/{lan}/artificials".format(lan=language))
        config_dict = get_config_dict(config, language)
        target_fit = pd.read_csv("data/params/real/{language}_params.csv".format(language=language))
        
        decay_intercept, decay_rate = target_fit['a (homophone decay intercept)'].values[0], target_fit['b (homophone decay rate)'].values[0]

        # Get info to generate lexicon
        info_for_generation = preprocess_lexicon(language)

        for mode in ['anti_homophones', 'neutral']:
            lexica = []
            print("Building lexica for '{mode}' mode".format(mode=mode))

            # og_dist = info_for_generation['original_counts'].copy()
            # for k in og_dist.keys():
            #    og_dist[k] = round(og_dist[k] / 100)

            for lex in range(config.ITERATIONS):
                builder = LexiconBuilder(language=config_dict['language'],
                             length_dist = info_for_generation['original_counts'],
                             lm = info_for_generation['model'],
                             match_on=config_dict['match_on'],
                             vowels=config_dict['vowels'],
                             mode=mode,
                             decay_rate = decay_rate,
                             decay_intercept = decay_intercept
                             )
                df_lexicon = builder.build_lexicon(lex_num=lex)
                lexicon = pd.DataFrame(builder.lexicon.create_dict())
                lexicon['mode'] = mode
                lexicon.to_csv("data/processed/{lan1}/artificials/lex{lex}_matched_on_{match}_mode_{mode}_{n}phone.csv".format(
                lan1=language, lex=lex, match=config_dict['match_on'],
                mode=mode, n=config_dict['n']))

                lexica.append(lexicon)

            df_combined = pd.concat(lexica)
            df_combined.to_csv("data/processed/{lan1}/artificials/all_artificials_{N}_matched_on_{match}_mode_{mode}_{n}phone.csv".format(
                lan1=language, N=config.ITERATIONS, match=config_dict['match_on'],
                mode=mode, n=config_dict['n']))

    # raise NotImplementedError

def get_real_params_for_each_language():
    """Assuming each real lexicon has been preprocessed and analyzed, extract parameters."""
    for language in LANGUAGES:
        print("Fitting params for {lan}".format(lan=language))
        params = get_analysis_parameters(config, language=language)
        analyzer = Analyzer(**params)
        analyzer.load_real_lexica()
        analyzer.get_real_params()


def main(mode):
    """Run specified mode."""
    mode_to_func = {
        'extract_reals': get_real_params_for_each_language,
        'generate': generate_lexica
    }
    print(mode)
    func = mode_to_func[mode]
    func()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run analysis.')
    parser.add_argument('--mode', default='extract_reals', type=str,
                        help='Extract real parameters for each language')

    args = vars(parser.parse_args())

    main(**args)