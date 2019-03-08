"""Utility functions for preprocessing and analysis"""


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