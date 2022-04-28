"""Class for preprocessing lexicons."""

import numpy as np
import pandas as pd

from collections import Counter
from sklearn.model_selection import LeaveOneOut, train_test_split, KFold
from tqdm import tqdm

import src.config as config
import src.utils as utils
from src.generative_model import *

from src.minimal_pairs import find_minimal_pairs_lazy




### TODO: Preprocessor should also extract/count #minimal pairs for the real lexicon and save that info.


### Utility function
def get_config_dict(config, language):

    return {'language': language,
            'phon_column': config.PHON_COLUMN[language],
            'word_column': config.WORD_COLUMN[language],
            'vowels': config.VOWEL_SETS[language],
            'match_on': config.MODEL_INFO['match_on'],
            'phonetic_remappings': config.PHONETIC_REMAPPINGS[language],
            'n': config.MODEL_INFO['n'],
            'smoothing': config.MODEL_INFO['smoothing']}


### Class for preprocessing raw data files
class Preprocessor(object):

    def __init__(self, language, phonetic_remappings, phon_column, word_column, 
                 vowels, n, smoothing, match_on):
        self.language = language
        self.df_original = self.load_original(language)
        self.phonetic_remappings = phonetic_remappings
        self.phon_column = phon_column
        self.word_column = word_column
        self.vowels = vowels
        print("N-phone set to: {n}".format(n=n))
        self.n = n
        self.smoothing = smoothing
        self.match_on = match_on
        self.setup()


    def load_original(self, language):
        path, sep = config.LEXICON_PATHS[language]
        return pd.read_csv(path, sep=sep)

    def setup(self):
        if self.language in ['english', 'german', 'english_polysemy']:
            ## TODO: Identify proper nouns?
            self.df_preprocessed = self.df_original.copy()
            self.df_preprocessed['PhonDISC'] = self.df_preprocessed['PhonDISC'].apply(lambda x: self.remap_transcription(x))
        elif self.language in ["french", 'french_polysemy']:
            ## TODO: Remove proper nouns? ['4_cgram']!='PRO:per']
            self.df_preprocessed = self.df_original[self.df_original['14_islem']==1]
        elif self.language in ['dutch', 'dutch_polysemy']:
            self.df_preprocessed = self.df_original.dropna()
            self.df_preprocessed['PhonDISC'] = self.df_preprocessed['PhonStrsDISC'].apply(lambda x: self.remove_celex_stress(x))
            self.df_preprocessed['PhonDISC'] = self.df_preprocessed['PhonDISC'].apply(lambda x: self.remap_transcription(x))
        elif self.language in ['japanese']:
            self.df_preprocessed = self.df_original[self.df_original['morph_form']!="prop"]
            self.df_preprocessed['multiple_pronunications'] = self.df_preprocessed['phonetic_form'].apply(lambda x: "/" in x)
            self.df_preprocessed = self.df_preprocessed[self.df_preprocessed['multiple_pronunications']==False]
            self.df_preprocessed['phonetic_remapped'] = self.df_preprocessed['phonetic_form'].apply(lambda x: self.remap_transcription(x))
        elif self.language in ['mandarin']:
            print("{X} wordforms.".format(X=len(self.df_original)))
            ## Get proper noun orthographic representations from SUBTLEX
            proper_nouns = utils.load_subtlex_for_proper_nouns()
            print("{X} proper noun orthographic representations.".format(X = len(proper_nouns)))
            ## Remove proper nouns from lexicon
            self.df_original = self.df_original[~self.df_original['word'].isin(proper_nouns)]
            print("{X} wordforms in lexicon after removing proper nouns.".format(X=len(self.df_original)))
            ## Also remove any that we missed from this initial pass
            POS_TO_REMOVE = ['nr', 'ns', 'nt', 'nz']
            self.df_original = self.df_original[~self.df_original['Dominate-POS'].isin(POS_TO_REMOVE)]
            print("{X} wordforms after second pass of removing: place names, personal names, organization names, and other proper nouns.".format(X=len(self.df_original)))

            print("Remapping apostrophes...")
            self.df_original['IPA+T'] = self.df_original['IPA+T'].apply(lambda x: x.replace("ʻ", "'"))
            print("Remapping glides")
            self.df_original['glides_remapped'] = self.df_original['IPA+T'].apply(lambda x: self.remap_glides(x))
            print("Remapping diphthongs")
            self.df_original['phonetic_remapped'] = self.df_original['glides_remapped'].apply(lambda x: self.remap_transcription(x))
            print("Removing spaces from wordforms")
            self.df_original['phonetic_remapped'] = self.df_original['phonetic_remapped'].apply(lambda x: x.replace(" ", ""))
            self.df_preprocessed = self.df_original.copy()

        elif self.language in ['mandarin_cld', 'mandarin_polysemy']:
            print("{X} wordforms in Chinese Lexical Database (CLD).".format(X=len(self.df_original)))
            self.df_preprocessed = self.df_original.copy()
            ## Get proper noun orthographic representations from SUBTLEX
            proper_nouns = utils.load_subtlex_for_proper_nouns()
            print("{X} proper noun orthographic representations.".format(X = len(proper_nouns)))
            ## Remove from CLD
            self.df_preprocessed = self.df_preprocessed[~self.df_preprocessed['Word'].isin(proper_nouns)]
            print("{X} wordforms in CLD after removing proper nouns.".format(X=len(self.df_preprocessed)))

            # Remap transcription
            self.df_preprocessed['phonetic_remapped'] = self.df_preprocessed['Pinyin'].apply(lambda x: self.remap_transcription(x))

        # Drop any NA words
        self.df_preprocessed = self.df_preprocessed.dropna(subset=[self.word_column])

    def remove_celex_stress(self, wordform):
        """Remove stress markers to create unstressed version."""
        return wordform.replace("'", "").replace("-", "")

    def remap_transcription(self, wordform):
        """Remap any phonemes represented by double characters to single characters."""
        for og, new in self.phonetic_remappings.items():
            wordform = wordform.replace(og, new)
        return wordform

    def remap_glides(self, wordform, possible_glides=['i', 'u', 'y']):
        """Identify medial glides and remap them to the character G."""
        new_wordform = ''
        i = 0
        mandarin_vowels = self.vowels
        while i < len(wordform):
            letter = wordform[i]
            if letter in possible_glides:
                if (i+1) < len(wordform) and wordform[i+1] in mandarin_vowels:
                    new_wordform += 'G'
                    i += 1
                    continue
            
            # Otherwise, add letter
            new_wordform += letter
            i += 1
        return new_wordform

    def obtain_length_distribution(self, dataframe, match_on="phones"):
        """Obtain length distribution."""
        if match_on == 'phones':
            return Counter(list(dataframe['num_phones']))
        elif match_on == 'sylls':
            return Counter(list(dataframe['num_sylls_est']))

    def create_model(self, wordforms, n=5, smoothing=.01):
        """Create n-gram model."""
        lm = NgramModel(n, wordforms, 1)
        lm.create_model(wordforms, smoothing)
        return lm


    def remove_word(self, word):
        """Tag word for removal."""
        return " " in word or "-" in word or "'" in word

    def remove_words(self, df_lexicon):
        """Remove words with hyphens, spaces, etc."""
        df_lexicon['remove'] = df_lexicon[self.word_column].apply(lambda x: self.remove_word(x))
        df_lexicon = df_lexicon[df_lexicon['remove']==False]
        return df_lexicon

    def aggregate_over_wordforms(self, df_lexicon, word_column, phon_column):
        """Preprocess dataframe for analysis."""

        # Get #homophones per wordform
        homophone_counts = df_lexicon.groupby(phon_column).size() - 1

        # Add info to main dataframe
        df_lexicon['num_homophones'] = df_lexicon[phon_column].apply(lambda x: homophone_counts[x])

        # Remove duplicate wordforms
        df_lexicon = df_lexicon.drop_duplicates(subset=phon_column)

        return df_lexicon


    def get_minimal_pairs(self):
        """Find minimal pairs for all wordforms."""
        neighborhood_sizes = find_minimal_pairs_lazy(self.df_processed[self.phon_column].values)
        self.df_processed['neighborhood_size'] = self.df_processed[self.phon_column].apply(lambda x: neighborhood_sizes[x])
        print("Saving dataframe with minimal pairs...")
        print("data/processed/{lang1}/reals/{lang2}_with_mps_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))
        self.df_processed.to_csv("data/processed/{lang1}/reals/{lang2}_with_mps_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))


    def calculate_heldout_surprisal(wordforms, n=5, smoothing=.01, num_folds=10):
        """Calculate surprisal of words using holdout / cross-validation."""

        # Make sure wordforms is np.array
        wordforms = np.array(wordforms)

        # Set up cross-validation
        kf = KFold(n_splits=num_folds)
        splits = list(kf.split(wordforms))

        held_out_data = []

        for train_indices, test_indices in tqdm(splits):
            train = wordforms[train_indices]
            test = wordforms[test_indices]

            # Set up model
            lm = NgramModel(n, wordforms, 1)
            lm.create_model(train, smoothing)

            for i in test:
                held_out_data.append({
                    'word': i,
                    'heldout_surprisal': -lm.evaluate(i)[-1],
                    'heldout_log_prob': lm.evaluate(i)[-1]
                })
        
        return pd.DataFrame(held_out_data)




    def preprocess_lexicon(self, verbose=True, remove=True):
        """Preprocess Celex dataframe."""
        if verbose:
            print("Original count: {x} entries".format(x=len(self.df_preprocessed)))
        self.df_preprocessed['num_phones'] = self.df_preprocessed[self.phon_column].apply(lambda x: len(x))
        self.df_preprocessed['num_sylls_est'] = self.df_preprocessed[self.phon_column].apply(lambda x: utils.count_syllables(x, language=self.language, vowels=self.vowels))


        # Remove Japanese words >10 syllables
        if self.language == 'japanese':
            self.df_preprocessed = self.df_preprocessed[self.df_preprocessed['num_sylls_est']<=10]
            print(len(self.df_preprocessed))
            print("After removing words >10 syllables: {x} entries".format(x=len(self.df_preprocessed)))

        # Remove words estimates to have <1 syllables.
        self.df_preprocessed = self.df_preprocessed[self.df_preprocessed['num_sylls_est'] > 0]
        if verbose:
            print("After removing words with <1 syllable: {x} entries".format(x=len(self.df_preprocessed)))

        # Remove words with hyphens, etc. (if remove=True)
        self.df_preprocessed = self.remove_words(self.df_preprocessed)
        if verbose:
            print("After removing words with hyphens and spaces: {x} entries".format(x=len(self.df_preprocessed)))

        # Obtain estimate of counts for original lexicon
        original_counts = self.obtain_length_distribution(self.df_preprocessed, match_on=self.match_on)

        # Get aggregated dataframe
        self.df_processed = self.aggregate_over_wordforms(self.df_preprocessed, word_column=self.word_column, phon_column=self.phon_column).reset_index()
        unique_counts = self.obtain_length_distribution(self.df_processed, match_on=self.match_on)
        if verbose:
            print("After aggregating over homophonous wordforms: {x} entries".format(x=len(self.df_processed)))

        # Build n-gram model.
        print("Creating phonotactic model...")
        unique_wordforms = list(self.df_processed[self.phon_column])
        model = self.create_model(unique_wordforms, n=self.n, smoothing=self.smoothing)

        # Obtain surprisal estimates
        self.df_processed['log_prob'] = self.df_processed[self.phon_column].apply(lambda x: model.evaluate(x)[2])
        self.df_processed['surprisal'] = self.df_processed['log_prob'].apply(lambda x: -x)
        self.df_preprocessed['log_prob'] = self.df_preprocessed[self.phon_column].apply(lambda x: model.evaluate(x)[2])
        self.df_preprocessed['surprisal'] = self.df_preprocessed['log_prob'].apply(lambda x: -x)

        # Get homophone ranks
        self.df_processed['rank_num_homophones'] = self.df_processed['num_homophones'].rank(ascending=False, method="first")

        # Get unique phonemes
        phonemes = list(set(''.join(self.df_processed[self.phon_column].values)))



        # Save dataframes to file
        print("Saving dataframes to file...")
        print("data/processed/{lang1}/reals/{lang2}_all_reals_{n}phone.csv".format(lang1=self.language, lang2=self.language, n = self.n))
        self.df_preprocessed.to_csv("data/processed/{lang1}/reals/{lang2}_all_reals_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))
        print("data/processed/{lang1}/reals/{lang2}_lemmas_processed_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))
        self.df_processed.to_csv("data/processed/{lang1}/reals/{lang2}_lemmas_processed_{n}phone.csv".format(lang1=self.language, lang2=self.language, n=self.n))

        return {'model': model,
                'original_counts': original_counts,
                'unique_counts': unique_counts,
                'original_lexicon': unique_wordforms,
                'phonemes': phonemes,
                'surprisals': self.df_processed['surprisal'].values,
                'homophone_rank_distribution': dict(self.df_processed[['rank_num_homophones', 'num_homophones']].values)}
                # 'neighborhood_rank_distribution': dict(self.df_processed[['rank_neighborhood_size', 'neighborhood_size']].values)}



