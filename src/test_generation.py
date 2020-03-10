"""Code for generating artificial lexica with streamlined classes."""

import config 
import pandas as pd

import utils

from preprocessor import Preprocessor, get_config_dict
from lexicon_builder import LexiconBuilder



### Extract params
config_dict = get_config_dict(config)

preprocessor = Preprocessor(**config_dict)
preprocessor.setup()

info_for_generation = preprocessor.preprocess_lexicon()


## For testing
og_dist = info_for_generation['original_counts']
for k in og_dist.keys():
	og_dist[k] = round(og_dist[k] / 50)


builder = LexiconBuilder(language=config_dict['language'],
						 length_dist = og_dist, ## info_for_generation['original_counts'],
						 lm = info_for_generation['model'],
						 match_on=config_dict['match_on'],
						 vowels=config_dict['vowels']
						 )


builder.setup()

## Traditional (though class-based) builder
df_lexicon = builder.build_lexicon(lex_num=1)

## Lexicon obtained via graph structure, alrady contains neighborhood sizes
alt_lexicon = pd.DataFrame(builder.lexicon.create_dict())


## Compare lexica to make sure they're roughly the same
df_processed = utils.preprocess_for_analysis(df_lexicon, word_column="word", phon_column="word", remove=False)
s = alt_lexicon[df_processed.columns]
g = s.reset_index(drop=True) == df_processed.reset_index(drop=True)

