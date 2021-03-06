"""Config file."""


LANGUAGE = 'japanese' # 

LEXICON_PATHS = {'english': ['data/raw/english/celex_all.csv', '\\'],
				 'french': ['data/raw/french/french_lexique.txt', '\t'],
				 'german': ['data/raw/german/celex_german_all.csv', '\\'],
				 'japanese': ['data/raw/japanese/japanese_labeled_columns.csv', None], # formatting fixed, with column labels
				 'dutch': ['data/raw/dutch/celex_dutch.csv', '\\'] # Need to fix some issues with formatting
				 }


# try different n-phone models
MODEL_INFO = {'n': 4, 'smoothing': .01, 
			  'match_on': 'sylls' # phones vs. sylls
			  }

ITERATIONS = 10 # number to generate

# http://www.iub.edu/~psyling/papers/celex_eug.pdf
# See pg. 179
VOWEL_SETS = {'german': set("i#a$u3y)eo|o1246WBXIYE/{&AVOU@^cq0~"), 
			  'english': set("i#$u312456789IE{QVU@cq0~"),
			  'dutch': set("i!auy()*<e|oKLMIEAO}@"),
		  	  'french': set("i5§yEO9a°e@2uo"),
		  	  'mandarin': set("i5§yEO9a°e@2uo"),
		  	  'japanese': set("aeiouEOIU12345YN") # Japanese includes "N", placeless nasal coda
		  		} 


PHON_COLUMN = {'german': 'PhonDISC',
			   'english': 'PhonDISC',
			   'dutch': 'PhonDISC',
			   'japanese': 'phonetic_remapped', # Requires remapping double-characters
			   'french': '2_phon'}

WORD_COLUMN = {'german': 'Word',
			   'english': 'Word',
			   'dutch': 'Word',
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
		'yu': 'Y' # Represents result of conversion from romaji to pronunciation field
		}
}		   

