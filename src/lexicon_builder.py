"""Class for building artificial lexica."""

import numpy as np
import random
import pandas as pd
from tqdm import tqdm


from src.utils import count_syllables, has_correct_tones, is_wellformed
from src.lexicon import Wordform, Edge, Lexicon


## TODO: Wrap utilities into their own class

class LexiconBuilder(object):

    def __init__(self, language, length_dist, lm, vowels, match_on, mode='neutral', 
                decay_rate=.5, decay_intercept=1, growth_rate=.5, growth_intercept=1):
        """Initialize class.

        Parameters
        ----------
        language: str
          the language being generated (e.g., "english")
        length_dist: dict
          a dictionary indicating the number of words in each bin of #syllables.
        lm: NgramModel
          a trained phonotactic model
        vowels: list
          set of allowable vowels for language
        match_on: str
          whether to match on #syllables or #phones
        mode: str
          one of {'neutral', 'anti_homophones', 'pro_neighborhoods'}
          currently unimplemented, but will operate in the following way:
            'neutral': p(add(word))=1 for all words satisfying #syllable requirements.
            'anti_homophones': p(add(word)) starts at/close to 1, decreases with #homophones.
            'pro_neighborhoods': p(add(word)) starts close to 0, increases with #neighborhoods.
        decay_rate: float
          parameterizes rate at which p(add(word)) decays with #homophones(word).
        growth_rate: float
          parameterizes rate at which p(add(word)) grows with #neighbors(word). 

        """
        self.language = language
        self.length_dist = length_dist
        self.lm = lm
        self.match_on = match_on
        self.vowels = vowels

        self.mode = mode

        self.set_parameters(mode=mode, decay_rate=decay_rate, decay_intercept=decay_intercept, growth_intercept=growth_intercept, growth_rate=growth_rate)
        self.setup()


    def setup(self):
        """Setup attributes."""
        self.artificial_lengths = self.length_dist.copy()
        self.new_lexicon = []
        self.new_words = []
        self.lexicon = Lexicon()

    def set_parameters(self, mode, decay_rate=.5, decay_intercept=1, growth_intercept=1, growth_rate=.5):
        """Set selection parameters."""
        self.setup()
        self.mode = mode
        self.decay_intercept = decay_intercept
        self.decay_rate = decay_rate
        self.growth_rate = growth_rate
        self.growth_intercept = growth_intercept


    def get_word_length(self, w):
        """Return integer reflecting word length."""
        num_sylls = count_syllables(w, language=self.language, vowels=self.vowels)
        word_length = len(w) if self.match_on == "phones" else num_sylls
        return word_length

    def build_lexicon(self, lex_num):
        """Build a lexicon according to the parameters."""
        with tqdm(total=sum(self.length_dist.values())) as progress_bar:
            while True:
                candidate = self.create_word()
                word_length = self.get_word_length(candidate)
                if self.satisfies_criteria(candidate) and self.add_word(candidate):

                    # Decrement required words of that length
                    self.artificial_lengths[word_length] -= 1

                    # Get word probability
                    prob = self.lm.evaluate(candidate)[2]

                    # Add to bank of words
                    self.new_lexicon.append(candidate)

                    # Count #syllables
                    num_sylls = count_syllables(candidate, language=self.language, vowels=self.vowels)

                    # Add to lexicon: og style
                    self.new_words.append({
                        'word': candidate,
                        'num_phones': len(candidate),
                        'prob': prob,
                        'num_sylls_est': num_sylls,
                        'surprisal': -prob,
                        'lexicon': lex_num,
                        'mode': self.mode
                        })

                    # Add word to lexicon graph: new style
                    word = Wordform(wordform=candidate, surprisal=-prob, num_sylls=num_sylls)
                    self.lexicon.add_word(word)

                    progress_bar.update(1)

                elif sum(self.artificial_lengths.values()) == 0:
                    return pd.DataFrame(self.new_words)


    def create_word(self):
        """Generate a word."""
        return self.lm.generate()[0]

    def satisfies_criteria(self, w):
        """Determines whether word satisfies minimal criteria to add. This does *not* include critera re: homophony
        or neighborhoods."""

        word_length = self.get_word_length(w)

        if self.language == 'mandarin':
            if not is_wellformed(w, vowels=self.vowels) or not has_correct_tones(w):
                return False

        return self.artificial_lengths[word_length] > 0 and any((v in self.vowels) for v in w)


    def add_word(self, w):
        """Determine whether to add word, as a function of the number of words sharing that form already."""
        if self.mode == 'neutral':
            return True
        
        if self.mode == 'anti_homophones':

            ## If the word isn't known, then return it automatically
            if w not in self.lexicon.words:
                return True

            entry = self.lexicon.words[self.lexicon.words.index(w)]
            num_homophones = entry.homophones + 1 ## To account for 0 entries
            probability = self.decay_intercept /(num_homophones**self.decay_rate)
 
            # Compare p to random value n between [0, 1]. If p>=n, add.
            # Logic: higher p should be more likely to be greater than random number n.
            return probability >= random.random() 

            ## TODO: add parameter to toggle 'transform' mode––instead of rejecting homophone outright, replace it with a minimal pair.

            ## TODO: could sample from np.random.binomial parameterized by probability, will add noise.

        elif self.mode == 'pro_neighborhoods':

            raise NotImplementedError("Neighborhood selection process not yet implemented.")
            ## TODO: Count number of neighbors of candidate word. 
            ## If word already exists in lexicon, this is easy.
            ## Otherwise, count how many neighbors word would have. And increase p(add(word)) at some rate relative to that.
            #### Unless we think it's non-monotonic or even inverse-U? I.e., some neighbors are good, up to a point?

        else:
            raise Exception("Mode {x} not known.".format(x=str(self.mode)))






