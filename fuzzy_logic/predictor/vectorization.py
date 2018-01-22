# -*- coding: utf-8 -*-
# Use Python 2.6+
# python my_twitter.py ../../../../keywords_politics_us.txt
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

from __future__ import division, print_function

import logging

import gensim
import numpy as np
import pandas as pd
from gensim.models.word2vec import Word2Vec
from keras.layers import Dense
from keras.models import Sequential
from nltk.tokenize import TweetTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import sys

sys.path.append('/home/mike/Desktop/repoo/information_diffusion/fuzzy_logic_engine')
from fuzzy_logic_engine import FuzzyModule

# Shows status bar
tqdm.pandas(desc="progress-bar")
# Gendsim model
LabeledSentence = gensim.models.doc2vec.LabeledSentence
# Tweet tokenizer from nltk
tokenizer = TweetTokenizer()
pd.options.mode.chained_assignment = None
# Tool for logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


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

# noinspection PyBroadException
def myTokenize(tweet):
    try:
        tweet = unicode(tweet.decode('utf-8').lower())
        tokens = tokenizer.tokenize(tweet)
        tokens = filter(lambda t: not t.startswith('@'), tokens)
        tokens = filter(lambda t: not t.startswith('#'), tokens)
        tokens = filter(lambda t: not t.startswith('http'), tokens)
        return tokens
    except:
        return 'NC'


def postprocessData(data, n=1000000):
    data = data.head(n)
    data['tokens'] = data['SentimentText'].progress_map(myTokenize)
    data = data[data.tokens != 'NC']
    data.reset_index(inplace=True)
    data.drop('index', inplace=True, axis=1)
    return data


def labelizeTweets(tweets, label_type):
    labelized = []
    for i, v in tqdm(enumerate(tweets)):
        label = '{}_{}'.format(label_type, i)
        labelized.append(LabeledSentence(v, [label]))
    return labelized


def buildWord2Vector(tokens, size, tweet_w2v=None, tfidf=None):
    vec = np.zeros(size).reshape((1, size))
    count = 0
    for word in tokens:
        try:
            vec += tweet_w2v[word].reshape((1, size)) + tfidf[word]
            count += 1
        except KeyError:
            continue
    if count != 0:
        vec /= count
    return vec


def main():

    # filename = './trainingandtestdata/testdata.manual.2009.06.14.csv'
    filename = '/home/mike/Desktop/data_set/trainingandtestdata/trainingandtestdata/training.1600000.processed.noemoticon.csv'

    nProb = 1000000
    nDim = 200

    data = dataHandler(filename)
    data = postprocessData(data, nProb)

    xTrain, xTest, yTrain, yTest = train_test_split(np.array(data.head(nProb).tokens), np.array(data.head(nProb).Sentiment), test_size=0.2)
    xTrain = labelizeTweets(xTrain, 'TRAIN')
    xTest = labelizeTweets(xTest, 'TEST')

    tweetW2V = Word2Vec(size=nDim, min_count=10)
    tweetW2V.build_vocab([x.words for x in tqdm(xTrain)])
    tweetW2V.train([x.words for x in tqdm(xTrain)], total_examples=tweetW2V.corpus_count, epochs=tweetW2V.iter)



    #print(tweetW2V.wmdistance())

    print("len: ")
    print(xTrain[0])
    print(len(xTrain[0]))

    print()
    'building tf-idf matrix ...'
    vectorizer = TfidfVectorizer( analyzer=lambda x: x, min_df=10 )
    matrix = vectorizer.fit_transform( [x.words for x in xTrain] )
    tfidf = dict( zip( vectorizer.get_feature_names(), vectorizer.idf_ ) )
    print()
    'vocab size :', len( tfidf )

    def buildWordVector (tokens, size):
        vec = np.zeros( size ).reshape( (1, size) )
        count = 0.
        for word in tokens:
            try:
                vec += tweetW2V[word].reshape( (1, size) )*tfidf[word]
                count += 1.
            except KeyError:  # handling the case where the token is not
                # in the corpus. useful for testing.
                continue
        if count != 0:
            vec /= count
        return vec

    from sklearn.preprocessing import scale
    train_vecs_w2v = np.concatenate( [buildWordVector( z, nDim ) for z in tqdm( map( lambda x: x.words, xTrain ) )] )
    train_vecs_w2v = scale( train_vecs_w2v )

    test_vecs_w2v = np.concatenate( [buildWordVector( z, nDim ) for z in tqdm( map( lambda x: x.words, xTest ) )] )
    test_vecs_w2v = scale( test_vecs_w2v )

    model = Sequential()
    model.add( Dense( 32, activation='relu', input_dim=200 ) )
    model.add( Dense( 1, activation='sigmoid' ) )
    model.compile( optimizer='rmsprop',
                   loss='binary_crossentropy',
                   metrics=['accuracy'] )

    model.fit( train_vecs_w2v, yTrain, epochs=9, batch_size=32, verbose=2 )

    score = model.evaluate( test_vecs_w2v, yTest, batch_size=128, verbose=2 )
    print(score[1])

    fuzzyModule = FuzzyModule(0, 35, 10, 50)

    # for i in xrange(len(xTrain)):
    #    print(xTrain[i])
    #     fuzzyModule.setFollowers(10,  10, 50,  10,  50,  100, 50,  100, 250)
    #      fuzzyModule.setTweetText(10, 50, tweetW2V.vector_size(xTrain[i]), 100, 150, tweetW2V.vector_size(xTrain[i + 1]), 100, 150, tweetW2V.vector_size(xTrain[i + 2]))
    #     fuzzyModule.setPopularity( 10, 20, 30, 40, 50, 60, 70, 80, 90 )
    #     fuzzyModule.makeVariables()
    #     fuzzyModule.makeMemberFunctions()
    #     fuzzyModule.makeRules()
    #    print()
    #     print(tweetW2V.vector_size(xTrain[i]))
    #
    #     fuzzyModule.simulate(50, tweetW2V.vector_size(xTrain[i]))
    #
    # print(tweetW2V)
    #
    # print(tweetW2V['good'])
    # print(len(tweetW2V['good']))
    # print()
    # print(tweetW2V.most_similar('good'))
    # print(len(tweetW2V.most_similar( 'good')))
    # print()
    # print(tweetW2V.most_similar('bar'))
    # print(len(tweetW2V.most_similar( 'bar' ) ))
    # print()

    #print(tweetW2V.most_similar('facebook'))
    #print(tweetW2V.most_similar('iphone'))
    #
    # fuzzyModule = FuzzyModule(0, 35, 10, 50)
    # fuzzyModule.setFollowers(0,  10, 50,  10,  50,  100, 50,  100, 250)
    # fuzzyModule.setTweetText(10, 50, (len(tweetW2V['good'])), 100, 150, (len(tweetW2V['good'])), 150, 200, (len(tweetW2V['good'])))
    # fuzzyModule.setPopularity(10, 20, 30, 40,  50,  60,  70,  80, 90)
    #
    # fuzzyModule.makeVariables()
    # fuzzyModule.makeMemberFunctions()
    # fuzzyModule.makeRules()
    #
    # fuzzyModule.simulate(50, 240)

    # defining the chart
    # output_notebook()
    # plotTfidf = bp.figure(plot_width=700, plot_height=600, title="A map of 10000 word vectors",
    #                       tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
    #                       x_axis_type=None, y_axis_type=None, min_border=1)
    #
    # # getting a list of word vectors. limit to 10000. each is of 200 dimensions
    # word2Vectors = [tweetW2V[w] for w in tweetW2V.wv.vocab[:5000]]
    #
    # # dimensionality reduction. converting the vectors to 2d vectors
    # tsneModel = TSNE(n_components=2, verbose=1, random_state=0)
    # tsneW2V = tsneModel.fit_transform(word2Vectors)
    #
    # # putting everything in a dataframe
    # tsneDf = pd.DataFrame(tsneW2V, columns=['x', 'y'])
    # tsneDf['words'] = tweetW2V.wv.vocab[:5000]
    #
    # # plotting. the corresponding word appears when you hover on the data point.
    # plotTfidf.scatter(x='x', y='y', source=tsneDf)
    # hover = plotTfidf.select(dict(type=HoverTool))
    # hover.tooltips = {"word": "@words"}
    # figure()
    # show(plotTfidf)

    # if True:
    #     print 'building tf-idf matrix ...'
    #     #vectorTfidf = TfidfVectorizer(analyzer=lambda x_vec:x_vec, min_df=10)
    #     vectorTfidf = TfidfVectorizer(analyzer= lambda x: x, min_df=10)
    #     # matrix = vectorizer.fit_transform([x.words for x in xTrain])
    #     tfidf = dict(zip(vectorTfidf.get_feature_names(), vectorTfidf.idf_))
    #     print 'vocab size :', len(tfidf)
    #
    #     trainVectorW2V = np.concatenate([buildWord2Vector(z, nDim) for z in tqdm(map(lambda x_train:x_train.words, xTrain))])
    #     print(trainVectorW2V)
    #     trainVectorW2V = scale(trainVectorW2V)
    #
    #     testVectorW2V = np.concatenate([buildWord2Vector(z, nDim) for z in tqdm(map(lambda x_test:x_test.words, xTest))])
    #     testVectorW2V = scale(testVectorW2V)
    #
    #     model = Sequential()
    #     model.add(Dense(32, activation='relu', input_dim=200))
    #     model.add(Dense(1, activation='sigmoid'))
    #
    #     model.add(Activation(32, activation='relu', input_dim=200))
    #     model.add(Activation(1, activation="sigmoid"))
    #
    #     model.compile(optimizer='rmsprop',
    #                   loss='binary_crossentropy',
    #                   metrics=['accuracy'])
    #
    #     model.fit( trainVectorW2V, yTrain, epochs=20, batch_size=32, verbose=2 )
    #
    #     result = model.evaluate(testVectorW2V, yTest, batch_size=128, verbose=2)
    #     print result[1]


if __name__ == '__main__':
    main()