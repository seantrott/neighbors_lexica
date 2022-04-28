"""Config file."""

from collections import OrderedDict

LANGUAGE = 'mandarin_cld' # 

TARGET = 'num_homophones'
REGRESSORS = ['normalized_surprisal', 'num_sylls_est']

LEXICON_PATHS = {'english': ['data/raw/english/celex_all.csv', '\\'],
				 'french': ['data/raw/french/french_lexique.txt', '\t'],
				 'spanish': ['data/raw/spanish/spanish_subtlex.txt', None],
				 'german': ['data/raw/german/celex_german_all.csv', '\\'],
				 'mandarin': ['data/raw/mandarin/mandarin_with_tones_seg1.csv', None], 
				 'mandarin_cld': ['data/raw/mandarin_cld/chineselexicaldatabase2.1.csv', None], 
				 'japanese': ['data/raw/japanese/japanese_labeled_columns.csv', None], # formatting fixed, with column labels
				 'dutch': ['data/raw/dutch/celex_dutch.csv', '\\'], # Need to fix some issues with formatting
				 'english_polysemy': ['data/raw/english_polysemy/english_senses.csv', None],
				 'mandarin_polysemy': ['data/raw/mandarin_polysemy/mandarin_senses.csv', None],
				 'french_polysemy': ['data/raw/french_polysemy/french_senses.csv', None],
				 'dutch_polysemy': ['data/raw/dutch_polysemy/dutch_senses.csv', None]
				 }



# try different n-phone models
MODEL_INFO = {'n': 4, 'smoothing': .01, 
			  'match_on': 'sylls', # phones vs. sylls
			  }

ITERATIONS = 10 # number to generate

# http://www.iub.edu/~psyling/papers/celex_eug.pdf
# See pg. 179
VOWEL_SETS = {'german': set("i#a$u3y9eo7o1246WBXIYE/{&AVOU@^cq0~"), 
			  'english': set("i#$u312456789IE{QVU@cq0~"),
			  'dutch': set("i!auy96<e7oKLMIEAO}@"),
		  	  'french': set("i5§yEO9a°e@2uo"),
		  	  'mandarin': set('aeiouəɪuɛɨʊUIAEOy'),
		  	  'mandarin_cld': set('vuoiaeWPUAKLMIOVQEYCB'), 
		  	  'mandarin_polysemy': set('vuoiaeWPUAKLMIOVQEYCB'),
		  	  'english_polysemy': set("i#$u312456789IE{QVU@cq0~"),
		  	  'french_polysemy': set("i5§yEO9a°e@2uo"),
		  	  'dutch_polysemy': set("i!auy()*<e|oKLMIEAO}@"),
		  	  'japanese': set("aeiouEOIU12345YN") # Japanese includes "N", placeless nasal coda
		  		} 



mandar_cld_vowels = set('vuoiaeUAIOVQEY'), 


PHON_COLUMN = {'german': 'PhonDISC',
			   'english': 'PhonDISC',
			   'english_polysemy': 'PhonDISC',
			   'french_polysemy': '2_phon',
			   'dutch_polysemy': 'PhonDISC',
			   'mandarin_polysemy': 'phonetic_remapped',
			   'mandarin_cld': 'phonetic_remapped', ### Pinyin vs. IPA? (Need to set vowels properly for both)
			   'dutch': 'PhonDISC',
			   'mandarin': 'phonetic_remapped', # Decide on which phonetic representation to use. Should we remap first? Use tones or no?
			   'japanese': 'phonetic_remapped', # Requires remapping double-characters
			   'french': '2_phon'}

WORD_COLUMN = {'german': 'Word',
			   'english': 'Word',
			   'english_polysemy': 'Word',
			   'dutch_polysemy': 'Word',
			   'dutch': 'Word',
			   'mandarin': 'word',
			   'mandarin_cld': 'Word',
			   'mandarin_polysemy': 'Word',
			   'japanese': 'orth_form_romaji',
			   'french_polysemy': '3_lemme',
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
	'mandarin': OrderedDict({'uo': 'U', ## Should be ordered
                          'aɪ': 'I', 
                          'aʊ': 'A',
                          'eɪ': 'E',
                          'oʊ': 'O',
                          "tɕ'": 'Q', # sampa  
                          "tʂ'": 'C', # sampa  
                          "ts'": 'c', # sampa  
                          "tʂ": 'Z',
                          "ts": 'z',
                          'tɕ': 'J', # sampa
                          "p'": 'P',
                          "k'": 'K',
                          # "tʻ": 'T',
                          "t'": 'T'
        }),
	'mandarin_polysemy': OrderedDict({
		'iao': 'W',
		'uai': 'P',
		'ua': 'U',
		'ai': 'A',
		'iu': 'K',
		'ia': 'L',
		'ie': 'M', 
		'ui': 'I',
		'uo': 'O',
		'ou': 'V',
		'ue': 'C',
		've': 'B',
		'ao': 'Q',
		'ei': 'E',
		'io': 'Y'
		}),
	'mandarin_cld': OrderedDict({
		'iao': 'W',
		'uai': 'P',
		'ua': 'U',
		'ai': 'A',
		'iu': 'K',
		'ia': 'L',
		'ie': 'M', 
		'ui': 'I',
		'uo': 'O',
		'ou': 'V',
		'ue': 'C',
		've': 'B',
		'ao': 'Q',
		'ei': 'E',
		'io': 'Y'
		}),
    'english': {},
    'english_polysemy': {},
    'french_polysemy': {},
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
    },
    'dutch_polysemy': {
    ')': '9', # replace for REGEX check
    '+': '8', # replace for REGEX check
    '|': '7', # replace for REGEX check
    '*': '6' # replace for REGEX check (6 not a symbol in Dutch, but is for English/German)
    }
}		



#### Remappings for PatPho: used to preprocess wordforms before 
#### encoding them as phonological embeddings
#### TODO: Double-check all these in CELEX
# http://www.iub.edu/~psyling/papers/celex_eug.pdf
PATPHO_REMAPPINGS = {
	'english': {
	    '1': 'eI', #diphthong
	    '2': 'aI', #diphthong
	    '4': 'OI', #diphthong
	    '5': '@U', #diphthong
	    '6': '&U', #diphthong
	    '7': 'I@', #diphthong
	    '8': 'E@', #diphthong
	    '9': 'U@', #diphthong
	    '#': 'A', # long vowel (ignoring length for now)
	    '$': 'O', # long vowel (ignoring length for now)
	    '{': '&', # "pat"
	    '_': 'J', # abJect, Jeep, ...
	    'x': 'k', # uGH
	    ### Need to add syllabic consonsants from PhonDISC...not sure best way to do this.
	    'R': 'er', # fathER
	    'H': 'In', # burdEN
	    'P': 'Ul', # dangLE
	    'F': 'Vm', # idealisM
	    'C': 'Vn', # bacON
	    ### Nasalized vowels
	    'q': 'A', # detEnte
	    '~': 'Q', # buillOn
	    '0': 'A', # lIngerie
	    'c': '&', # tImbre 
	},
	'german': {
	    '1': 'eI', #diphthong
	    '2': 'aI', #diphthong
	    '4': 'OI', #diphthong
	    '5': '@U', #diphthong
	    '6': '&U', #diphthong
	    '7': 'I@', #diphthong
	    '8': 'E@', #diphthong
	    '9': 'U@', #diphthong
        'W': 'ai', #diphthong
        'B': 'au', #diphthong
	    '#': 'A', # long vowel (ignoring length for now)
	    '$': 'O', # long vowel (ignoring length for now)
	    '{': '&', # "pat"
	    '_': 'J', # abJect, Jeep, ...
	    'x': 'k', # uGH
	    ### Need to add syllabic consonsants from PhonDISC...not sure best way to do this.
	    'R': 'er', # fathER
	    'H': 'In', # burdEN
	    'P': 'Ul', # dangLE
	    'F': 'Vm', # idealisM
	    'C': 'Vn', # bacON
	    ### Nasalized vowels
	    'q': 'A', # detEnte
	    '~': 'Q', # buillOn
	    '0': 'A', # lIngerie
	    'c': '&', # tImbre 
	    ### Other consonants
	    '=': 'ts',
	    '8': 'pf', # + --> 9 --> pgf
        '-': 'J', # jeep
        ### Other short vowels
        'Y': 'u', ## not quite right, for ü (this transcribes to "boon")
        'o': 'O', ## not quite right, for "story"
        '/': '3', ## not quite right, for "hurt" 
        'y': 'U', ## not quite right, for "few" (für)
        'X': 'OU',
        '<': 'Q',
        '^': '3',
        '¬': ''


	}
}
