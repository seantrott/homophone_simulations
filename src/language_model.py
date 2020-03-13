"""Simple Markov model to build phonotactically-plausible words. Developed as an alternative to the model used in Dautriche et al (2016)."""


import pandas as pd
import random

class NullModel(object):

	def __init__(self, lexicon):
		"""Generates strings without regard to phonotactics."""
		self.lexicon = lexicon
		self.units = self.generate_units(lexicon)

	def generate_units(self, lexicon):
		"""Identify all unique tokens."""
		sounds = ''
		for word in lexicon:
			sounds += word
		unique_sounds = set(sounds)
		return list(unique_sounds)

	def create_word(self, n):
		"""Create word of length n."""
		word = ''
		for i in range(n):
			word += random.choice(self.units)
		return word


class PhonotacticModel(object):

	def __init__(self, lexicon):
		self.lexicon = lexicon




lexicon = pd.read_csv('data/raw/english/celex_all.csv', sep="\\")

nm = NullModel(lexicon['PhonDISC'])

nm.create_word(5)