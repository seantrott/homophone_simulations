"""Class for building artificial lexica."""

import pandas as pd
from tqdm import tqdm


from utils import count_syllables, has_correct_tones, is_wellformed
from lexicon import Wordform, Edge, Lexicon


## TODO: Wrap utilities into their own class

class LexiconBuilder(object):

    def __init__(self, language, length_dist, lm, vowels, match_on):
        """Initialize class.

        Parameters
        ----------
        language: str
          the language being generated (e.g., "english")
        length_dist: dict
          a dictionary indicating the number of words in each bin of #syllables.
        lm: NgramModel
          a trained phonotactic model

        """
        self.language = language
        self.length_dist = length_dist
        self.lm = lm
        self.match_on = match_on
        self.vowels = vowels
        self.setup()


    def setup(self):
        """Setup (or reset) attributes."""
        self.artificial_lengths = self.length_dist.copy()
        self.new_lexicon = []
        self.new_words = []

        self.lexicon = Lexicon()


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
                if self.satisfies_criteria(candidate):

                    # Decrement required words of that length
                    self.artificial_lengths[word_length] -= 1

                    # Get word probability
                    prob = self.lm.evaluate(candidate)[2]

                    # Add to bank of words
                    self.new_lexicon.append(candidate)

                    # Count #syllables
                    num_sylls = count_syllables(candidate, language=self.language, vowels=self.vowels)

                    # Add to lexicon
                    self.new_words.append({
                        'word': candidate,
                        'num_phones': len(candidate),
                        'prob': prob,
                        'num_sylls_est': num_sylls,
                        'surprisal': -prob,
                        'lexicon': lex_num
                        })

                    # Add word to lexicon object
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
        pass






