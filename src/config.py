"""Config file."""

from collections import OrderedDict

LANGUAGE = 'mandarin_cld' # 

TARGET = 'num_homophones'
REGRESSORS = ['normalized_surprisal', 'num_sylls_est']

LEXICON_PATHS = {'english': ['data/raw/english/celex_all.csv', '\\'],
				 'french': ['data/raw/french/french_lexique.txt', '\t'],
				 'spanish': ['data/raw/spanish/spanish_subtlex.txt', None],
				 'german': ['data/raw/german/celex_german_all.csv', '\\'],
				 'mandarin_cld': ['data/raw/mandarin_cld/chineselexicaldatabase2.1.csv', None], 
				 'dutch': ['data/raw/dutch/celex_dutch.csv', '\\'], # Need to fix some issues with formatting
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
		  	  'mandarin': set('aeiouəɪuɛɨʊUIAEOy'),
		  	  'mandarin_cld': set('vuoiaeWPUAKLMIOVQEYCB'), 
		  		} 


### Mandarin CLD Vowels
mandar_cld_vowels = set('vuoiaeUAIOVQEY'), 


PHON_COLUMN = {'german': 'PhonDISC',
			   'english': 'PhonDISC',
			   'mandarin_cld': 'phonetic_remapped', 
			   'dutch': 'PhonDISC',
			   'french': '2_phon'}

WORD_COLUMN = {'german': 'Word',
			   'english': 'Word',
			   'dutch': 'Word',
			   'mandarin_cld': 'Word',
			   'french': '3_lemme'}	



# Maybe preserve this so other languages can have remappings too?
PHONETIC_REMAPPINGS = {
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



#### Remappings for PatPho: used to preprocess wordforms before 
#### encoding them as phonological embeddings
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
