# -*- coding: utf-8 -*-
# Use Python 2.6+
# python my_twitter.py ../../../../keywords_politics_us.txt
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

import codecs
import datetime
import portalocker
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import time

from pattern.web import Twitter, hashtags

# This is the main data pattern (a set of words) which is used for mining the Tweets.
keywords = None

#######
# PARAMETERS START
#######

# Treat all keywords like hashtags
onlyHashTags = False

# Treat all keywords like separate words (cannot appear inside other words)
onlyWords = False

# Use False to match "AZ" with "az"
caseSensitive = False

# Tweets with fewer keywords won't appear on the list.
reqNKeywords = 1

# Sprinkles the keywords set with random typos in order to widen the search radius.
insertTypos = False

# Only the words having this length or higher are considered for typo generation.
minTypoLen = 5

# Restart the stream after the specified time, -1 to turn off.
restartInterval = 1000 # seconds

# Set to empty string not to dump the data.
filePath = os.path.expanduser("~") + "/Desktop/tweets.dat"
# filePath = ""

# English = "en", Polish = "pl" (doesn't really matter, most Tweets don't use it).
lang = "en"

pollTime = 5 # seconds

### LANGUAGE FILTERING OPTIONS
# Use only tweets from a given language based on the dictionary.
filterUsingDict = True
filterDict = None

# ENGLISH
dictPath = "/home/mike/Desktop/data_set/dictionary/american-english-insane.txt"

dictRatio = 0.5 # 0.5 means that 50% of the words must appear in the dictionary for a Tweet to pass.

#######
# PARAMETERS END
#######

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colorGreen(text):
    return Colors.OKGREEN + str(text) + Colors.ENDC

def setKeywords():
    with open(sys.argv[1], "r") as f:
        data = f.read()

    words = [d.strip() for d in data.split("\n") if d]
    words = [w.decode("utf-8") for w in words]

    nWords = len(words)

    if insertTypos:
        wordsWithTypos = []

        for w in words:
            if len(w) < minTypoLen:
                continue

            # We take all permutations of the words with one character missing.
            for i in xrange(len(w)):
                typoWord = w[ : i] + w[i + 1 : ]
                wordsWithTypos += [typoWord]

        words += wordsWithTypos
        print("Inserted typos, new #words = {0}, old #words = {1} (min len = {2})" \
              .format(len(words), nWords, minTypoLen))

    global keywords
    keywords = set(words)

    # Join with space for "AND"; join with "," for "OR".
    # If you want multiple keywords to appear, it is better to use the nReqKeywords parameter.
    return ", ".join(sorted(words)).encode("utf-8")

def dumpStats(elapsed, nTweets, nIgnored):
    nPolls = int(elapsed / pollTime)

    if elapsed > 0.0:
        avgNTweetsMin = float(nTweets) / (elapsed / 60.0)
    else:
        avgNTweetsMin = 0.0

    print("Total elapsed = {0}s ({1} poll(s) {2}s each)".format(round(elapsed), nPolls, pollTime))
    print("Total #tweets = {0}, avg per minute = {1}, total #ignored = {2}". \
          format(colorGreen(nTweets), colorGreen(round(avgNTweetsMin, 2)), nIgnored))

    if restartInterval != -1:
        remaining = restartInterval - int(elapsed)
        assert remaining >= 0

        print("Remaining = {0}s".format(remaining))

def strEqual(s1, s2):
    assert type(s1) == type(s2) == unicode

    if caseSensitive:
        return s1 == s2
    else:
        return s1.lower() == s2.lower()

def getKeywords(tweet):
    res = []

    if onlyHashTags:
        hashes = hashtags(tweet.text)

        for h in hashes:
            for k in keywords:
                if strEqual(h.strip("#"), k):
                    res += [h]
                    break
    elif onlyWords:
        words = getWordsStripped(tweet)

        for w in words:
            for k in keywords:
                if strEqual(w, k):
                    res += [w]
                    break
    else:
        res = getKeywordsSubstr(tweet.text)

    return list(set(res)) # We remove the duplicates.

def getKeywordsSubstr(text):
    res = set()

    # This is a naive algorithm, perhaps it would be worth changing if we get a lot of data (unlikely).
    for i in xrange(len(text)):
        for keyword in keywords:
            l = len(keyword)
            curText = text[i : i + l]

            if strEqual(curText, keyword):
                res.add(keyword)

    return res

def getWordsStripped(tweet):
    words = tweet.text.split()

    # If we use only words, we don't want some other stuff to get into the way (hashes, commas, etc).
    return [w.strip("#@,.:!?\"\' \t") for w in words if w]

def isKosher(tweet):
    assert reqNKeywords >= 1
    appeared = set(getKeywords(tweet))

    if len(appeared) < reqNKeywords:
        print("Ignored Tweet: {0} < {1} (appeared, required)".format(len(appeared), reqNKeywords))
        return False

    if filterUsingDict:
        words = getWordsStripped(tweet)

        # We also want to ignore the keywords --- these are usually names, etc, and they rarely appear in the dictionary.
        words = [w for w in words if w not in keywords]

        # Make sure to use lower case here, because dicts are usually lower case!
        appeared = [w for w in words if w.lower() in filterDict]
        nAppeared = len(appeared)

        assert 0.0 < dictRatio <= 1.0 and filterDict
        curRatio = float(nAppeared) / len(words)

        if curRatio < dictRatio:
            print "Ignored foreign Tweet: #appeared = {0}, #words = {1}, ratio: {2} < {3}, appeared = {4}" \
                  .format(nAppeared, len(words), curRatio, dictRatio, appeared)
            return False
        else:
            print "Passed: #appeared = {0}, #words = {1}, ratio: {2} >= {3}, appeared = {4}" \
                  .format(nAppeared, len(words), curRatio, dictRatio, appeared)

    return True

def tweetToFile(tweet, fPath):
    with open(fPath, "a") as f: # Append mode
        # We use a filelock here juuuust in case (it is unlocked automatically after the with block).
        portalocker.lock(f, portalocker.LOCK_EX)

        f.write(str(tweet) + "\n")
        f.write("Normalized text = \"{0}\"\n".format(tweet.text.encode("utf-8")))
        f.write("Keywords = {0}\n\n".format(sorted(getKeywords(tweet))))

def dumpTweets(stream, nIgnored):
    nTweets = 0

    hashList = []
    keywordsList = []

    curNIgnored = 0

    # The stream is a list of buffered tweets so far,
    # with the latest tweet at the end of the list.
    for tweet in reversed(stream):
        if not isKosher(tweet):
            curNIgnored += 1
            continue

        curKeywords = sorted(getKeywords(tweet))
        keywordsList += curKeywords
        nTweets += 1

        hashes = hashtags(tweet.text.encode("utf-8"))
        hashList += [hashes]

        if filePath:
           tweetToFile(tweet, filePath)

    print("\nPolled {0} tweets, #ignored (current) = {1}".format(nTweets, curNIgnored))
    print("Hash list = {0}, keywords (appeared) = {1}".format(hashList, sorted(keywordsList)))
    return nTweets

def doStream(stream):
    nTweets, nIgnored = 0, 0
    startTime = time.time()

    while True:
        # Poll Twitter to see if there are new tweets.
        stream.update()
        nTweets += dumpTweets(stream, nIgnored)

        elapsed = time.time() - startTime
        if restartInterval != -1 and elapsed >= restartInterval:
            return nTweets, nIgnored

        dumpStats(elapsed, nTweets, nIgnored)

        # Clear the buffer and wait awhile between polls.
        stream.clear()
        time.sleep(pollTime)

    return 0, 0

def setStream(keywordsStr):
    assert keywordsStr
    print("\n\n==== ====\n\n")
    print("Setting up the stream for keywords = {0}".format(keywords))
    print("\nKeywords Twitter QUERY = \"{0}\"".format(colorGreen(keywordsStr)))

    if filePath:
        print("Will dump to file: {0}".format(colorGreen(filePath)))
    else:
        print("No file dump")

    # It might take a few seconds to set up the stream.
    stream = Twitter(throttle = 0.5, language = lang).stream(keywordsStr, timeout = 30)
    print("\nStream initialized")

    return stream

def loadDict():
    sizeKB = round(float(os.stat(dictPath).st_size) / 1024.0, 2)
    print("Reading dictionary from: {0} (size = {1} KB)".format(dictPath, sizeKB))

    with open(dictPath) as f:
        data = f.read().split("\n")

    data = [d.strip().decode("utf-8") for d in data if d]
    return set(data)

def clearScreen():
    if os.name.lower() == "posix":
        os.system("clear")
    elif os.name.lower() == "nt":
        os.system("cls")

def main():
    if len(sys.argv) != 2:
        print("Usage: python my_twitter.py [keywords file]")
        sys.exit(1)

    clearScreen()
    keywordsStr = setKeywords()

    if filterUsingDict:
        global filterDict
        filterDict = loadDict()

        print("WARNING: FILTERING USING DICTIONARY (path = {0}, #words = {1}, ratio = {2})" \
              .format(dictPath, colorGreen(len(filterDict)), dictRatio))

    totalNTweets, totalNIgnored = 0, 0

    while True:
        try:
            stream = setStream(keywordsStr)
            print("Set up a new stream at {0}".format(datetime.datetime.now()))

            nTweets, nIgnored = doStream(stream)

            totalNTweets += nTweets
            totalNIgnored += nIgnored

            print("\nStream finished, #tweets = {0}, #ignored = {1}".format(nTweets, nIgnored))
        except Exception as e:
            # In case an exception is thrown (e.g., connection closed by a remote host) we just start over.
            print("Unexpected error: {0}, msg = {1}".format(sys.exc_info(), e.message))
            print("RESTARTING...\n\n")

if __name__ == "__main__":
    main()
