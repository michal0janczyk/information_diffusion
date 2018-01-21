# -*- coding: utf-8 -*-
# Use Python 2.6+
# python my_twitter.py ../../../../keywords_politics_us.txt
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

import argparse
import sklearn.utils
from sklearn.model_selection import cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.linear_model import LogisticRegression
from collections import defaultdict
from nltk.tokenize import TweetTokenizer

from my_tokenizer import glove_tokenize
from data_handler import getData

# Preparing the text data
# List of text samples
textsSamples = []
# Dictionary mapping label name to numeric id
labelsIndex = {}
# List of label ids
labels = []

# Vocabulary generation
vocab = {}
reverseVocab = {}
freqVocab = defaultdict(int)
tweets = {}

# tfidf_logistic, tfidf_gradient_boosting, tfidf_random_forest, tfidf_svm_linear, tfidf_svm_rbf
MODEL_TYPE = None
MAX_NGRAM_LENGTH = None
CLASS_WEIGHT = None
N_ESTIMATORS = None
LOSS_FUN = None
KERNEL = None
TOKENIZER = None
SEED = 42
NO_OF_FOLDS = 10


def genData():
    """
    :rtype: str
    """
    labelMap = {"none": 0,
                "racism": 1,
                "sexism": 2,
                "neutral": 3,
                "good": 4
                }
    tweetData = getData()
    for tweet in tweetData:
        assert isinstance(tweet, int)
        textsSamples.append(tweet["text"].lower())
        labels.append(labelMap[tweet["label"]])
    print("Text was fount at: %s (samples)" % len(textsSamples))


def getModel(modelType=None):
    """
    :param modelType:
    :return: logger
    :rtype: object, modelType
    """
    global logger
    if not modelType:
        print 'ERROR !!! Choose specifc model type'
        return None

    if modelType == "TFIDF_SVM":
        logger = SVC(class_weight=CLASS_WEIGHT, kernel=KERNEL)
    elif modelType == "TFIDF_SVM_LINEAR":
        logger = LinearSVC(C=0.01, loss=LOSS_FUN, class_weight=CLASS_WEIGHT)
    elif modelType == 'TFIDF_LOGISTIC':
        logger = LogisticRegression()
    elif modelType == "TFID_GRADIENT_BOOSTING":
        logger = GradientBoostingClassifier(loss=LOSS_FUN, n_estimators=N_ESTIMATORS)
    elif modelType == "TFIDF_RANDOM_FOREST":
        logger = RandomForestClassifier(class_weight=CLASS_WEIGHT, n_estimators=N_ESTIMATORS)
        print "ERROR !!! Please specify a correct model"
        return None

    return logger


def classificationModel(X, Y, modelType=None):
    X, Y = sklearn.utils.shuffle(X, Y, random_state=SEED)
    print "Model Type:", modelType

    # Predictions = cross_val_predict(logger, X, Y, cv=NO_OF_FOLDS)
    resPrec = cross_val_score(getModel(modelType), X, Y, cv=NO_OF_FOLDS, scoring="precision_weighted")
    print "Precision(avg): {:0.3f} (+/- {:0.3f})".format(resPrec.mean(), resPrec.std()*2)

    resRec = cross_val_score(getModel(modelType), X, Y, cv=NO_OF_FOLDS, scoring='recall_weighted')
    print "Recall(avg): {:0.3f} (+/- {:0.3f})".format(resRec.mean(), resRec.std()*2)

    resF1 = cross_val_score(getModel(modelType), X, Y, cv=NO_OF_FOLDS, scoring='f1_weighted')
    print "F1-score(avg): {:0.3f} (+/- {:0.3f})".format(resF1.mean(), resF1.std()*2)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='TF-IDF model for twitter Hate speech detection')
    parser.add_argument('--model', choices=['tfidf_svm',
                                                  'tfidf_svm_linear',
                                                  'tfidf_logistic',
                                                  'tfidf_gradient_boosting',
                                                  'tfidf_random_forest'], required=True)
    parser.add_argument('--max_ngram', required=True)
    parser.add_argument('--tokenizer', choices=['glove', 'nltk'], required=True)
    parser.add_argument('--seed', default=SEED)
    parser.add_argument('--folds', default=NO_OF_FOLDS)
    parser.add_argument('--estimators', default=N_ESTIMATORS)
    parser.add_argument('--loss', default=LOSS_FUN)
    parser.add_argument('--kernel', default=KERNEL)
    parser.add_argument('--class_weight')
    parser.add_argument('--use-inverse-doc-freq', action='store_true')

    args = parser.parse_args()

    MODEL_TYPE = args.model
    SEED = int(args.seed)
    NO_OF_FOLDS = int(args.folds)
    CLASS_WEIGHT = args.class_weight
    N_ESTIMATORS = int(args.estimators) if args.estimators else args.estimators
    LOSS_FUN = args.loss
    KERNEL = args.kernel
    MAX_NGRAM_LENGTH = int(args.max_ngram)
    USE_IDF = args.use_inverse_doc_freq

    if args.tokenizer == "glove":
        TOKENIZER = glove_tokenize
    elif args.tokenizer == "nltk":
        TOKENIZER = TweetTokenizer().tokenize

    print "Max-ngram-length: {:d}".format( MAX_NGRAM_LENGTH )

    # For TFIDF-SVC or any other varient
    # We do not need to run the above code for TFIDF
    # It does not use the filtered data using gen_data()
    genData()
    tfidfTransformer = TfidfVectorizer(use_idf=USE_IDF,
                                       analyzer="word",
                                       tokenizer=TOKENIZER,
                                       ngram_range=(1, MAX_NGRAM_LENGTH))

    # tfidf_transformer = TfidfVectorizer(use_idf=True, ngram_range=(1, MAX_NGRAM_LENGTH))
    xTrainTfidf = tfidfTransformer.fit_transform(textsSamples)
    X = xTrainTfidf
    Y = labels

    classificationModel(X, Y, MODEL_TYPE)
