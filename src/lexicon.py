"""Class for representing lexicon as a graph structure. Each wordform is a node, and each minimal pair
is connected via an edge."""

import re

from src.minimal_pairs import generate_mp_regex


class Wordform(object):

	def __init__(self, wordform, surprisal, num_sylls):
		self.wordform = wordform
		self.surprisal = surprisal
		self.num_sylls = num_sylls
		self.num_phones = len(self.wordform)

		self.neighbors = []
		self.homophones = 0
		

	def __repr__(self):
		return self.wordform

	def __eq__(self, target):
		return self.wordform == target

	def add_entry(self):
		self.homophones += 1

	def add_neighbor(self, w2):
		# new_edge = Edge(self, w2)
		self.neighbors.append(w2)



class Edge(object):

	def __init__(self, w1, w2):
		self.w1 = w1
		self.w2 = w2

	def __repr__(self):
		return "{w1} <--> {w2}".format(w1=self.w1.wordform, w2=self.w2.wordform)

	def __eq__(self, target):
		return self.w1 == target.w1 and self.w2 == target.w2


class Lexicon(object):
	"""Class for representing lexicon as a graph structure."""

	def __init__(self):
		self.words = []
		self.edges = []

	def add_word(self, word):
		"""Add word to lexicon."""
		if word in self.words:
			target = self.words[self.words.index(word)]
			target.add_entry()
		else:
			self.get_neighbors(word)
			self.words.append(word)


	def get_neighbors(self, word):
		"""Get neighbors of word."""
		regex = re.compile(generate_mp_regex(word.wordform))
		# matches = [w.wordform for w in self.words if w not in seen and regex.match(w)]
		matches = [w for w in self.words if regex.match(w.wordform) and w.wordform != word.wordform]
		for neighbor in matches:
			new_edge = Edge(word, neighbor)
			self.edges.append(new_edge)
			neighbor.add_neighbor(word)
			word.add_neighbor(neighbor)

	def create_dict(self, lex_num=1):
		"""Turn Lexicon object into dictionary."""
		dict_repr = []
		for w in self.words:
			dict_repr.append({
				'word': w.wordform,
                'num_phones': w.num_phones,
                'prob': -w.surprisal,
                'num_sylls_est': w.num_sylls,
                'surprisal': w.surprisal,
                'lexicon': lex_num,
                'num_homophones': w.homophones,
                'neighborhood_size': len(w.neighbors)
				})

		return dict_repr

	def __repr__(self):
		"""Returns string representation of lexicon."""
		r = ""
		for i in self.words:
			r += "{w1}: {x} homophones\n".format(w1=i.wordform, x=i.homophones)
			if len(i.neighbors) > 0:
				r += "  neighbors:\n"
				for n in i.neighbors:
					r += "    {x}\n".format(x=n.wordform)
		return r


### TODO: Check that this approach returns the same # as the other minimal pair functions







