import cython
import nltk, re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer
english_stops             = stopwords.words('english')
english_stops.remove('not')



def tokenize(raw_text):
	standard_tokenizer =  CountVectorizer().build_tokenizer()
	tokens             =  standard_tokenizer(raw_text)
	return tokens

def get_custom_stopwords():
	stop_doc  = "data/stopwords"
	with open(stop_doc, 'r') as stopfile:
		custom_stops   = nltk.word_tokenize(stopfile.read())
	stopfile.close()
	return custom_stops

def emails_and_urls(raw_text):
	email_stops   = set()
	url_pattern  = r'[\[\<]*[A-Za-z]+[:.]+\S+'
	url_regexp   = re.compile(url_pattern)
	for words in url_regexp.findall(raw_text):
		email_stops.add(words)
	return list(email_stops)

def phone_nums(raw_text):
	phone_stops    = []
	phone_regexp   = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')

	for words in phone_regexp.findall(raw_text):
		phone_stops.append(words)
	return phone_stops


def unused_nums_and_text(raw_text):
	num_stops = []
	reg_nums = re.compile(r'[a-zA-Z]*[0-9]+[a-zA-Z]*')
	for words in reg_nums.findall(raw_text):
		num_stops.append(words)

	reg_text = re.compile(r'[A-Z]+[\_A-Z]+')
	for words in reg_text.findall(raw_text):
		num_stops.append(words)
	return num_stops

def named_entities(raw_text):
	stop_names  = extract_names(raw_text)
	return stop_names

def ie_preprocess(document):
	document = ' '.join([i for i in document.split() if i not in english_stops])
	sentences = nltk.sent_tokenize(document)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	return sentences

def extract_names(document):
	names = []
	sentences = ie_preprocess(document)
	for tagged_sentence in sentences:
		for chunk in nltk.ne_chunk(tagged_sentence):
			if type(chunk) == nltk.tree.Tree:
				if chunk.label() == 'LOCATION' or chunk.label() == 'ORGANIZATION' or chunk.label() == 'DATE' or chunk.label() == 'FACILITY' or chunk.label() == 'TIME':
					names.extend([c[0] for c in chunk])
	return names

def stanfordNER(raw_text):
	name_stops   = []
	tagged_text  = stanf_tagger.tag(nltk.word_tokenize(raw_text)) #st.tag(raw_text.split())
	for term, tag in tagged_text:
		if(tag == 'LOCATION' or tag == 'ORGANIZATION' or tag == 'GPE' or tag == 'DATE' or tag == 'FACILITY' or tag == 'TIME'):
			name_stops.append(term)
	return name_stops

def remove_punctuation(raw_text):
	text      = re.sub('[^A-Za-z0-9]',' ', raw_text)
	raw_text  = ' '.join(text.split())
	return raw_text


def get_clean_text(raw_text):
	raw_text = ' '.join(raw_text.split())
	all_stopwords  = []
	all_stopwords.extend(emails_and_urls(raw_text))
	all_stopwords.extend(phone_nums(raw_text))
	#print(all_stopwords)
	all_stops_removed  = ' '.join([word for word in raw_text.split() if word not in all_stopwords])

	#print('\n\n ---------------Removing Email, Phones -------------------- \n\n')
	#print(all_stops_removed)

	raw_text            = ' '.join(tokenize(all_stops_removed))

	all_stopwords       = []
	all_stopwords.extend(unused_nums_and_text(raw_text))
	#print(all_stopwords)
	all_stops_removed   = ' '.join([word for word in raw_text.split() if word not in all_stopwords])
	#print('\n\n --------------- Removing unused Numbers -------------------- \n\n')
	#print(all_stops_removed)

	raw_text                = all_stops_removed
	all_stopwords           = []
	all_stopwords.extend(extract_names(raw_text))
	#all_stopwords.extend(stanfordNER(raw_text))

	#print('\n\n ---------------- Removing Names ----------------------- \n\n')
	all_stops_removed            = ' '.join([word.lower() for word in raw_text.split() if word not in all_stopwords])
	#print(all_stops_removed)


	raw_tokens               = tokenize(all_stops_removed)
	stop_doc                 = 'test_corpus/stopwords'
	custom_stops             = [word.lower() for word in get_custom_stopwords()]

	filtered_tokens 	 = [term for term in raw_tokens if term not in custom_stops]
	#print('\n\n ----------------Removing Custom Stops------------------- \n\n')
	#print(' '.join(filtered_tokens))

	processed_tokens         = [word for word in filtered_tokens if word not in english_stops]

	#print('\n\n ---------------- Removing English Stops ----------------- \n\n')
	text                     = ' '.join(processed_tokens)
	#print("Cleaning...")
	clean_text               = remove_punctuation(text)
	return clean_text

