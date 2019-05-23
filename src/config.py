"""Config file."""


LANGUAGE = 'english' # 

LEXICON_PATHS = {'english': ['data/raw/english/celex_all.csv', '\\'],
				 'french': ['data/raw/french/french_lexique.txt', '\t'],
				 'spanish': ['data/raw/spanish/spanish_subtlex.txt', None],
				 'german': ['data/raw/german/celex_german_all.csv', '\\'],
				 'chinese': ['data/raw/chinese/SUBTLEX-CH-WF.txt', None], # Need to fix formatting issue
				 'dutch': ['data/raw/dutch/celex_dutch.csv', '\\'] # Need to fix some issues with formatting
				 }

"""Others:
Greek: https://www.bcbl.eu/subtlex-gr/
Polish: http://crr.ugent.be/programs-data/subtitle-frequencies/subtlex-pl
Brazilian Portuguese: http://crr.ugent.be/programs-data/subtitle-frequencies/subtlex-pt-br
Mandarin Chinese: https://catalog.ldc.upenn.edu/LDC96L15
Japanese: https://catalog.ldc.upenn.edu/LDC96L17

Open lexical databases: https://chrplr.github.io/openlexicon/databases-docs/

Also: http://www.cjk.org/cjk/samples/jpd_e.htm
"""

MODEL_INFO = {'n': 5, 'smoothing': .01, 
			  'match_on': 'sylls' # phones vs. sylls
			  }

ITERATIONS = 10 # number to generate

# http://www.iub.edu/~psyling/papers/celex_eug.pdf
# See pg. 179
VOWEL_SETS = {'german': set("i#a$u3y)eo|o1246WBXIYE/{&AVOU@^cq0~"), 
			  'english': set("i#$u312456789IE{QVU@cq0~"),
			  'dutch': set("i!auy()*<e|oKLMIEAO}@"),
		  	  # 'french': set("auioeEO@1589"), # And others?
		  	  'french': set("IE{VQU@i#$u312456789cq0~iI1!eE2@aAoO3#4$6^uU7&5+8*9(0)<>[]") # taken from Dautriche, prob too many
		  	  # 'french': set("aE§oOi@°y9@"),
		  		} 




