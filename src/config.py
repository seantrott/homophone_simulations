"""Config file."""


LANGUAGE = 'english' # 

TARGET = 'num_homophones'
REGRESSORS = ['normalized_surprisal', 'num_sylls_est']

LEXICON_PATHS = {'english': ['data/raw/english/celex_all.csv', '\\'],
				 'french': ['data/raw/french/french_lexique.txt', '\t'],
				 'spanish': ['data/raw/spanish/spanish_subtlex.txt', None],
				 'german': ['data/raw/german/celex_german_all.csv', '\\'],
				 'mandarin': ['data/raw/mandarin/mandarin_with_tones_seg1.csv', None], # Need to fix formatting issue
				 'japanese': ['data/raw/japanese/japanese_labeled_columns.csv', None], # formatting fixed, with column labels
				 'dutch': ['data/raw/dutch/celex_dutch.csv', '\\'] # Need to fix some issues with formatting
				 }


# Language parameters
### For each language, extract the fit parameters from power law, 
### as well as descriptive stats (e.g., max # homophones in real lexicon).
### Then fit a DECAY RATE that optimizes for these parameters.
FIT_PARAMETERS = {
	'english': {
	'a': None,
	'b': None,
	'max': None
	}
}

# try different n-phone models
MODEL_INFO = {'n': 5, 'smoothing': .01, 
			  'match_on': 'sylls', # phones vs. sylls
			  }

ITERATIONS = 10 # number to generate

# http://www.iub.edu/~psyling/papers/celex_eug.pdf
# See pg. 179
VOWEL_SETS = {'german': set("i#a$u3y)eo|o1246WBXIYE/{&AVOU@^cq0~"), 
			  'english': set("i#$u312456789IE{QVU@cq0~"),
			  'dutch': set("i!auy()*<e|oKLMIEAO}@"),
		  	  'french': set("i5§yEO9a°e@2uo"),
		  	  'mandarin': set('aeiouəɪuɛɨʊUIAEOy'),
		  	  'japanese': set("aeiouEOIU12345YN") # Japanese includes "N", placeless nasal coda
		  		} 


PHON_COLUMN = {'german': 'PhonDISC',
			   'english': 'PhonDISC',
			   'dutch': 'PhonDISC',
			   'mandarin': 'phonetic_remapped', # Decide on which phonetic representation to use. Should we remap first? Use tones or no?
			   'japanese': 'phonetic_remapped', # Requires remapping double-characters
			   'french': '2_phon'}

WORD_COLUMN = {'german': 'Word',
			   'english': 'Word',
			   'dutch': 'Word',
			   'mandarin': 'word',
			   'japanese': 'orth_form_romaji',
			   'french': '3_lemme'}	

# Maybe preserve this so other languages can have remappings too?
PHONETIC_REMAPPINGS = {
	'japanese': {
		'ky': 'K', # Already converted in pronuncation field
		'gy': 'G', # Already converted in pronuncation field
		'sh': 'S', # Already converted in pronuncation field
		'ch': 'C', # Already converted in pronuncation field
		'ts': 'c', # Already converted in pronuncation field
		'ny': 'Y', # Already converted in pronuncation field
		'hy': 'H', # Already converted in pronuncation field
		'by': 'B', # Already converted in pronuncation field
		'py': 'P', # Already converted in pronuncation field
		'my': 'M', # Already converted in pronuncation field
		'ry': 'R', # Already converted in pronuncation field
		'ee': 'E', # Represents result of conversion from romaji to pronunciation field
		'oo': 'O', # Represents result of conversion from romaji to pronunciation field
		'ji': 'I', # Represents result of conversion from romaji to pronunciation field
		'zu': 'U', # Represents result of conversion from romaji to pronunciation field
		'ue': '1', # Represents result of conversion from romaji to pronunciation field
		'ui': '2', # Represents result of conversion from romaji to pronunciation field
		'uo': '3', # Represents result of conversion from romaji to pronunciation field
		'ua': '4', # Represents result of conversion from romaji to pronunciation field
		'ie': '5', # Represents result of conversion from romaji to pronunciation field
		'yu': 'Y', # Represents result of conversion from romaji to pronunciation field
		'?': '9' # Replace for REGEX check
		},
	'mandarin': {'uo': 'U', ## Each of these remaps a Mandarin diphthong to a single character.
        'aɪ': 'I', 
        'aʊ': 'A',
        'eɪ': 'E',
        'oʊ': 'O'
        },
    'english': {},
    'french': {},
    'german': {
    ')': '9', # replace for REGEX check
    '+': '8', # replace for REGEX check
    '|': '7'
    },
    'dutch': {
    ')': '9', # replace for REGEX check
    '+': '8', # replace for REGEX check
    '|': '7', # replace for REGEX check
    '*': '6' # replace for REGEX check (6 not a symbol in Dutch, but is for English/German)
    }
}		   

