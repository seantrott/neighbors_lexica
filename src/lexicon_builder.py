"""Class for building artificial lexica."""

import random
import re

import numpy as np
import pandas as pd
from tqdm import tqdm

from src.utils import count_syllables, has_correct_tones, is_wellformed
from src.lexicon import Wordform, Edge, Lexicon


## TODO: Wrap utilities into their own class



def re_split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)

class LexiconBuilder(object):

    def __init__(self, language, length_dist, lm, vowels, match_on, rank_distribution, 
                 original_lexicon, surprisals, phonemes, mode='neutral'):
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
        rank_distribution: dict
          dictionary mapping number of homophones per word of that rank
        surprisals: array
          list of surprisal values from original distribution
        phonemes: array
          allowable phonemes in language
        mode: str
          one of {'neutral', 'anti_homophones', 'pro_neighborhoods'}
          currently unimplemented, but will operate in the following way:
            'neutral': p(add(word))=1 for all words satisfying #syllable requirements.
            'anti_homophones': p(add(word)) starts at/close to 1, decreases with #homophones.
            'pro_neighborhoods': p(add(word)) starts close to 0, increases with #neighborhoods.

        """
        self.language = language
        self.length_dist = length_dist
        self.lm = lm
        self.match_on = match_on
        self.vowels = list(vowels)
        self.phonemes = phonemes
        self.mode = mode

        self.set_parameters(mode=mode, rank_distribution=rank_distribution, surprisals=surprisals, original_lexicon=original_lexicon)
        self.setup()


    def setup(self):
        """Setup attributes."""
        self.artificial_lengths = self.length_dist.copy()
        self.new_lexicon = []
        self.new_words = []
        self.lexicon = Lexicon()

        self.consonants = [i for i in self.phonemes if i not in self.vowels]
        print(self.consonants)

    def set_parameters(self, mode, rank_distribution, surprisals, original_lexicon):
        """Set selection parameters."""
        self.setup()
        self.mode = mode
        self.rank_distribution = rank_distribution
        self.surprisals = surprisals
        self.original_lexicon = original_lexicon


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

                if self.satisfies_criteria(candidate):

                    w = self.add_word(candidate)
                    if w:
                        word_length = self.get_word_length(w)

                        # Decrement required words of that length
                        self.artificial_lengths[word_length] -= 1

                        # Get word probability
                        prob = self.lm.evaluate(w)[2]

                        # Add to bank of words
                        self.new_lexicon.append(w)

                        # Count #syllables
                        num_sylls = count_syllables(w, language=self.language, vowels=self.vowels)

                        # Add to lexicon: og style
                        self.new_words.append({
                            'word': w,
                            'num_phones': len(w),
                            'prob': prob,
                            'num_sylls_est': num_sylls,
                            'surprisal': -prob,
                            'lexicon': lex_num,
                            'mode': self.mode
                            })

                        # Add word to lexicon graph: new style
                        word = Wordform(wordform=w, surprisal=-prob, num_sylls=num_sylls)
                        self.lexicon.add_word(word)

                        progress_bar.update(1)

                # elif sum(self.artificial_lengths.values()) < 10:
                #    raise Exception("Fix this!!!")

                elif sum(self.artificial_lengths.values()) == 0:
                    return pd.DataFrame(self.new_words)


    def create_word(self):
        """Generate a word."""
        return self.lm.generate()[0]

    def is_wellformed(self, w):
        """Is word well-formed?

        For Mandarin words, split on tone characters, then make sure each syllable is
        actually 1 syllable in length (e.g., has exactly one vowel character). 

        TODO: Also check consonant/glide structure?
        """
        if self.language != 'mandarin':
            return True

        # Split word on tone characters, e.g., 'te0' --> ['te', '']
        tone_pattern = '|'.join(['0', '1', '2', '3', '4'])
        sylls = re.split(tone_pattern, w, 0)

        # Regex for wellformed syllable: optional consonant, optional glide, vowel, optional nasal
        # syll_pattern = '*[G][{vowels}]'.format(vowels=' '.join(self.vowels))
        syll_pattern = '^.?G?[{vowels}][nŋɹ]?$'.format(vowels=' '.join(self.vowels))

        # Split on tone characters
        for syll in sylls[0:-1]:
            # Make sure each interval has exactly one vowel character, e.g., is truly one syllable.
            if count_syllables(syll, language='mandarin', vowels=self.vowels) != 1:
                # print(syll)
                return False

            # Check that there aren't multiple consonants in a row
            # I.e., syllable should have optional consonant at beginning, optional glide, 
            # required vowel, and optional nasal at ending
            match = re.match(syll_pattern, syll)
            if not match:
                return False


        return True

    def has_correct_tones(self, w):
        """Checks whether word in Mandarin has correct tones and placement of tones."""
        raise Exception

    def satisfies_criteria(self, w):
        """Determines whether word satisfies minimal criteria to add. This does *not* include critera re: homophony
        or neighborhoods."""

        word_length = self.get_word_length(w)

        if self.language == 'mandarin':
            if not self.is_wellformed(w): # or not has_correct_tones(w):
                return False

        return self.artificial_lengths[word_length] > 0 and any((v in self.vowels) for v in w)


    def add_word(self, w):
        """Determine whether to add word, as a function of the number of words sharing that form already.

        Returns word if it's okay, returns None otherwise"""
        if self.mode == 'neutral':
            return w
        
        elif self.mode == 'anti_homophones':
            ## New method: use rank distribution

            if w not in self.lexicon.words:
                return w

            entry = self.lexicon.words[self.lexicon.words.index(w)]
            num_homophones = entry.homophones

            # Generate a lexicon from current set of words.
            current_lexicon = pd.DataFrame(self.lexicon.create_dict())
            current_lexicon['rank_num_homophones'] = current_lexicon['num_homophones'].rank(ascending=False, method="first")

            ## Get rank of highest-ranked word with same # homophones
            max_rank = current_lexicon[current_lexicon['num_homophones']==num_homophones]['rank_num_homophones'].min()

            # If word already has >=1 entry, yet is ranked *lower* than the number of words
            # in the original lexicon, don't add it
            if max_rank not in self.rank_distribution:
                return None

            # How many homophones does the N-th ranked word have in real lexicon?
            allowable_homophones = self.rank_distribution[max_rank]

            # If you can add more homophones, do so. 
            if allowable_homophones > num_homophones:
                return w
            else: 
                return None

        elif self.mode == 'anti_homophones_plus':
            ## New method: use rank distribution

            if w not in self.lexicon.words:
                return w

            entry = self.lexicon.words[self.lexicon.words.index(w)]
            num_homophones = entry.homophones

            # Generate a lexicon from current set of words.
            current_lexicon = pd.DataFrame(self.lexicon.create_dict())
            current_lexicon['rank_num_homophones'] = current_lexicon['num_homophones'].rank(ascending=False, method="first")

            ## Get rank of highest-ranked word with same # homophones
            max_rank = current_lexicon[current_lexicon['num_homophones']==num_homophones]['rank_num_homophones'].min()

            # If word already has >=1 entry, yet is ranked *lower* than the number of words
            # in the original lexicon, don't add it
            if max_rank not in self.rank_distribution:
                w2 = self.convert_to_neighbor(w)
                return self.add_word(w2)

            # How many homophones does the N-th ranked word have in real lexicon?
            allowable_homophones = self.rank_distribution[max_rank]

            # If you can add more homophones, do so. Otherewise, create a minimal pair
            if allowable_homophones > num_homophones:
                return w
            else: 
                ### TODO: For Japanese, possibly just stop trying this for single-character words...
                if self.language == "japanese" and len(w) == 1:
                    return None
                w2 = self.convert_to_neighbor(w)
                return self.add_word(w2)

        elif self.mode == 'pro_neighborhoods':

            raise NotImplementedError("Neighborhood selection process not yet implemented.")
            ## TODO: Count number of neighbors of candidate word. 
            ## If word already exists in lexicon, this is easy.
            ## Otherwise, count how many neighbors word would have. And increase p(add(word)) at some rate relative to that.
            #### Unless we think it's non-monotonic or even inverse-U? I.e., some neighbors are good, up to a point?

        elif self.mode == "real_only":

            ## Return True/False as a function of whether word is in the real (training) lexicon
            return w in self.original_lexicon

        else:
            raise Exception("Mode {x} not known.".format(x=str(self.mode)))



    def convert_to_neighbor(self, w):
        """Converts word to a near neighbor using a random edit."""

        while True:
            ## First select random index of word
            index = random.randrange(0, len(w))

            ## determine whether to replace with either vowel or consonant
            replacement_vector = self.vowels if w[index] in self.vowels else self.consonants

            ## Then sample random replacement
            replacement_token = random.choice([k for k in replacement_vector if k != w[index]])

            ## now replace
            w_list = list(w)
            w_list[index] = replacement_token
            new_word = ''.join(w_list)

            print(new_word)

            ## check for satisfaction of surprisal
            surprisal = -self.lm.evaluate(new_word)[2]
            if surprisal < max(self.surprisals):
                ## if surprisal is low enough, add to dictionary
                break
            else:
                print("Surprisal too high!!!")
        return new_word

