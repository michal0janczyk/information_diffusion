# -*- coding: utf-8 -*-
# Use Python 2.6+
# python my_twitter.py ../../../../keywords_politics_us.txt
# ALL STRINGS SHOULD BE HANDLED AS UTF-8!

import csv
import codecs
import cStringIO
import json
import pandas as pd


#######
# PARAMETERS START
#######

testDataPath = "/home/mike/Documents/Data sets/#testdat/trainingandtestdata/testdata.manual.2009.06.14.csv"
# data_json = open('raw_tweets.json', mode='r').read()  # reads in the JSON file into Python as a string
# data_python = json.loads(data_json)  # turns the string into a json Python object

#######
# PARAMETERS END
#######


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """

    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def csvPdReader(fPath):
    """
    Read a csv file
    """
    df = pd.read_csv(fPath, usecols=[5])
    print(df)
    df.to_csv("test.pickle", sep=' ', encoding='utf-8', index=False)


def csvPdRead(fPath):
    with open(fPath, 'rb') as csvfile:
        # get number of columns
        for line in csvfile.readlines():
            array = line.split(',')
            first_item = array[0]

        num_columns = len(array)
        csvfile.seek(0)

        reader = csv.reader(csvfile, delimiter=' ')
        included_cols = [7]

        for row in reader:
            content = list(row[i] for i in included_cols)
            print content


def csvParser(file):
    reader = csv.DictReader(
        file, delimiter=',', quotechar='"', escapechar='\\')
    tweets = []
    for row in reader:
        tweets.append(row['tweets'])


def csvWriter(fPath):
    # Opens csv file
    csv_out = open('tweets_out_ASCII.csv', mode='w')
    # Create the csv writer object
    writer = csv.writer(csv_out)
    # Field names
    fields = [
        'created_at', 'text', 'screen_name', 'followers', 'friends', 'rt',
        'fav'
    ]
    writer.writerow(fields)  # Writes field
    for line in data_python:
        # Writes a row and gets the fields from the json object
        # Screen_name and followers/friends are found on the second level hence two get methods
        writer.writerow([
            line.get('created_at'),
            # Unicode escape to fix emoji issue
            line.get('text').encode('unicode_escape'),
            line.get('user').get('screen_name'),
            line.get('user').get('followers_count'),
            line.get('user').get('friends_count'),
            line.get('retweet_count'),
            line.get('favorite_count')
        ])

    csv_out.close()

    with open(fPath, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(d)


def main():
    csvPdReader(testDataPath)


if __name__ == "__main__":
    main()
