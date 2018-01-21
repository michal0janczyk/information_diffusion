import matplotlib as plt

import nltk

from nltk.tokenize import sent_tokenize

text='Statistics skills, and programming skills are equally important for analytics. Statistics skills, and domain knowledge are important for analytics. I like reading books and travelling.'

# sent_tokenize uses an instance of PunktSentenceTokenizer from the nltk. tokenize.punkt module. This instance has already been trained on and works well for many European languages. So it knows what punctuation and characters mark the end of a sentence and the beginning of a new sentence.
sent_tokenize_list = sent_tokenize(text)
print(sent_tokenize_list)

# There are total 17 european languages that NLTK support for sentence tokenize
# Let's try loading a spanish model
import nltk.data
spanish_tokenizer = nltk.data.load('tokenizers/punkt/spanish.pickle')
spanish_tokenizer.tokenize('Hola. Esta es una frase espanola.')

from nltk.tokenize import word_tokenize
print word_tokenize(text)

# Another equivalent call method
from nltk.tokenize import TreebankWordTokenizer
tokenizer = TreebankWordTokenizer()

print tokenizer.tokenize(text)

# Except the TreebankWordTokenizer, there are other alternative word tokenizers, such as PunktWordTokenizer and WordPunktTokenizer
# PunktTokenizer splits on punctuation, but keeps it with the word
# from nltk.tokenize import PunktWordTokenizer
# punkt_word_tokenizer = PunktWordTokenizer()
# print punkt_word_tokenizer.tokenize(text)

# WordPunctTokenizer splits all punctuations into separate tokens
from nltk.tokenize import WordPunctTokenizer
word_punct_tokenizer = WordPunctTokenizer()
print word_punct_tokenizer.tokenize(text)

from nltk import chunk

tagged_sent = nltk.pos_tag(nltk.word_tokenize('This is a sample English sentence'))
print tagged_sent

tree = chunk.ne_chunk(tagged_sent)
tree.draw()

# To get help about tags
nltk.help.upenn_tagset('NNP')

from nltk.tag.perceptron import PerceptronTagger

PT = PerceptronTagger()
print PT.tag('This is a sample English sentence'.split())

from nltk.corpus import stopwords

# Function to remove stop words
def remove_stopwords(text, lang='english'):
    words = nltk.word_tokenize(text)
    lang_stopwords = stopwords.words(lang)
    stopwords_removed = [w for w in words if w.lower() not in lang_stopwords]
    return " ".join(stopwords_removed)

print remove_stopwords('This is a sample English sentence')

import string

# Function to remove punctuations
def remove_punctuations(text):
    words = nltk.word_tokenize(text)
    punt_removed = [w for w in words if w.lower() not in string.punctuation]
    return " ".join(punt_removed)

print remove_punctuations('This is a sample English sentence, with punctuations!')

import re

# Function to remove whitespace
def remove_whitespace(text):
    return " ".join(text.split())

# Function to remove numbers
def remove_numbers(text):
    return re.sub(r'\d+', '', text)

text = 'This 	is a     sample  English   sentence, \n with whitespace and numbers 1234!'
print 'Original Text: ', text
print 'Removed whitespace: ', remove_whitespace(text)
print 'Removed numbers: ', remove_numbers(text)

from nltk import PorterStemmer, LancasterStemmer, SnowballStemmer


# Function to apply stemming to a list of words
def words_stemmer (words, type="PorterStemmer", lang="english", encoding="utf8"):
    supported_stemmers = ["PorterStemmer", "LancasterStemmer", "SnowballStemmer"]
    if type is False or type not in supported_stemmers:
        return words
    else:
        stem_words = []
        if type == "PorterStemmer":
            stemmer = PorterStemmer()
            for word in words:
                stem_words.append( stemmer.stem( word ).encode( encoding ) )
        if type == "LancasterStemmer":
            stemmer = LancasterStemmer()
            for word in words:
                stem_words.append( stemmer.stem( word ).encode( encoding ) )
        if type == "SnowballStemmer":
            stemmer = SnowballStemmer( lang )
            for word in words:
                stem_words.append( stemmer.stem( word ).encode( encoding ) )
        return " ".join( stem_words )


words = 'caring cares cared caringly carefully'

print "Original: ", words
print "Porter: ", words_stemmer( nltk.word_tokenize( words ), "PorterStemmer" )
print "Lancaster: ", words_stemmer( nltk.word_tokenize( words ), "LancasterStemmer" )
print "Snowball: ", words_stemmer( nltk.word_tokenize( words ), "SnowballStemmer" )

from nltk.stem import WordNetLemmatizer

wordnet_lemmatizer = WordNetLemmatizer()

# Function to apply lemmatization to a list of words
def words_lemmatizer(text, encoding="utf8"):
    words = nltk.word_tokenize(text)
    lemma_words = []
    wl = WordNetLemmatizer()
    for word in words:
        pos = find_pos(word)
        lemma_words.append(wl.lemmatize(word, pos).encode(encoding))
    return " ".join(lemma_words)

# Function to find part of speech tag for a word
def find_pos(word):
    # Part of Speech constants
    # ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v'
    # You can learn more about these at http://wordnet.princeton.edu/wordnet/man/wndb.5WN.html#sect3
    # You can learn more about all the penn tree tags at https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    pos = nltk.pos_tag(nltk.word_tokenize(word))[0][1]
    # Adjective tags - 'JJ', 'JJR', 'JJS'
    if pos.lower()[0] == 'j':
        return 'a'
    # Adverb tags - 'RB', 'RBR', 'RBS'
    elif pos.lower()[0] == 'r':
        return 'r'
    # Verb tags - 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'
    elif pos.lower()[0] == 'v':
        return 'v'
    # Noun tags - 'NN', 'NNS', 'NNP', 'NNPS'
    else:
        return 'n'

print "Lemmatized: ", words_lemmatizer(words)

from nltk.corpus import wordnet

syns = wordnet.synsets("good")
print "Definition: ", syns[0].definition()
print "Example: ", syns[0].examples()

synonyms = []
antonyms = []

# Print  synonums and antonyms (having opposite meaning words)
for syn in wordnet.synsets("good"):
    for l in syn.lemmas():
        synonyms.append(l.name())
        if l.antonyms():
            antonyms.append(l.antonyms()[0].name())

print "synonyms: \n", set(synonyms)
print "antonyms: \n", set(antonyms)

# n-grams
from nltk.util import ngrams
from collections import Counter

# Function to extract n-grams from text
def get_ngrams(text, n):
    n_grams = ngrams(nltk.word_tokenize(text), n)
    return [ ' '.join(grams) for grams in n_grams]

text = 'This is a sample English sentence'

print "1-gram: ", get_ngrams(text, 1)
print "2-gram: ", get_ngrams(text, 2)
print "3-gram: ", get_ngrams(text, 3)
print "4-gram: ", get_ngrams(text, 4)

text = 'Statistics skills, and programming skills are equally important for analytics. Statistics skills, and domain knowledge are important for analytics'

# remove punctuations
text = remove_punctuations(text)

# Extracting bigrams
result = get_ngrams(text,2)

# Counting bigrams
result_count = Counter(result)

print "Words: ", result_count.keys() # Bigrams
print "\nFrequency: ", result_count.values() # Bigram frequency

# Converting to the result to a data frame
import pandas as pd
df = pd.DataFrame.from_dict(result_count, orient='index')
df = df.rename(columns={'index':'words', 0:'frequency'}) # Renaming index and column name
print df


import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Create a dictionary with key as file names and values as text for all files in a given folder
def CorpusFromDir(dir_path):
    result = dict(docs = [open(os.path.join(dir_path,f)).read() for f in os.listdir(dir_path)],
               ColNames = map(lambda x: x, os.listdir(dir_path)))
    return result

def dataHandler(filename):
    data = pd.read_csv(filename, header=None)
    data.drop([1, 2, 3, 4], axis=1, inplace=True)
    data = data.rename(columns={0: 'Sentiment'})
    data = data.rename(columns={5: 'SentimentText'})


    data = data[data.Sentiment.isnull() == False]
    #data['Sentiment'] = data['Sentiment'].map(int)

    #assert isinstance(data, int)
    data['Sentiment'] = data['Sentiment'].map({4:1, 0:0})
    data = data[data['SentimentText'].isnull() == False]
    data.reset_index(inplace=True)
    data.drop('index', axis=1, inplace=True)
    return data

df = dataHandler('/home/mike/Desktop/data_set/trainingandtestdata/trainingandtestdata/training.1600000.processed.noemoticon.csv')

# Initialize
vectorizer = CountVectorizer()
#doc_vec = vectorizer.fit_transform(docs.get('docs'))

#create dataFrame
#df = pd.DataFrame(docs, index=vectorizer.get_feature_names())

#df = pd.DataFrame(docs.transpose(), index = vectorizer.get_feature_names())

# Change column headers to be file names
#df.columns = docs.get('ColNames')
print df


from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
doc_vec = vectorizer.fit_transform(df.get('docs'))
#create dataFrame
df = pd.DataFrame(doc_vec.toarray().transpose(), index = vectorizer.get_feature_names())

# Change column headers to be file names
df.columns = df.get('ColNames')
print df


