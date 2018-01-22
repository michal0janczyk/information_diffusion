import multiprocessing
from multiprocessing import Process
from cleanup import TwitterCleanuper
from preprocessing import TwitterData
from word2vec import Word2VecProvider
import pandas as pd

def preprocess(results, data_path, is_testing, data_name, min_occurrences=5, cache_output=None):
    twitter_data = TwitterData()
    twitter_data.initialize(data_path, is_testing)
    twitter_data.build_features()
    twitter_data.cleanup(TwitterCleanuper())
    twitter_data.tokenize()
    twitter_data.build_wordlist(min_occurrences=min_occurrences)
    twitter_data.build_data_model()
    # twitter_data.build_ngrams()
    # twitter_data.build_ngram_model()
    # twitter_data.build_data_model(with_ngram=2)
    word2vec = Word2VecProvider()
    word2vec.load("/home/mike/Desktop/glove.twitter.27B.200d.txt")
    twitter_data.build_word2vec_model(word2vec)
    if cache_output is not None:
        twitter_data.data_model.to_csv(cache_output, index_label="idx", float_format="%.6f")
    results[data_name] = twitter_data.data_model


def preprare_data(min_occurrences):
    import os
    training_data = None
    testing_data = None
    print("Loading data...")
    test_data_file_name = "data/processed_test_word2vec_bow_" + str(min_occurrences) + ".csv"
    train_data_file_name = "data/processed_train_word2vec_bow_" + str(min_occurrences) + ".csv"
    use_cache = os.path.isfile(train_data_file_name) and os.path.isfile(
        test_data_file_name)
    if use_cache:
        training_data = TwitterData()
        training_data.initialize(None, from_cached=train_data_file_name)
        training_data = training_data.data_model

        testing_data = TwitterData()
        testing_data.initialize(None, from_cached=test_data_file_name)
        testing_data = testing_data.data_model
        print("Loaded from cached files...")
    else:
        print("Preprocessing data...")
        with multiprocessing.Manager() as manager:

            results = manager.dict()

            preprocess_training = Process(target=preprocess, args=(
                results, "data/train.csv", False, "train", min_occurrences, train_data_file_name,))

            preprocess_testing = Process(target=preprocess, args=(
                results, "data/train.csv", True, "test", min_occurrences, test_data_file_name,))

            preprocess_training.start()
            preprocess_testing.start()
            print("Multiple processes started...")

            preprocess_testing.join()
            print("Preprocessed testing data...")

            preprocess_training.join()
            print("Preprocessed training data...")

            training_data = results["train"]
            testing_data = results["test"]

            print("Data preprocessed & cached...")

    return training_data, testing_data


class TwitterData( TwitterData_ExtraFeatures ):

    def build_final_model (self, word2vec_provider, stopwords=nltk.corpus.stopwords.words( "english" )):
        whitelist = self.whitelist
        stopwords = list( filter( lambda sw: sw not in whitelist, stopwords ) )
        extra_columns = [col for col in self.processed_data.columns if col.startswith( "number_of" )]
        similarity_columns = ["bad_similarity", "good_similarity", "information_similarity"]
        label_column = []
        if not self.is_testing:
            label_column = ["label"]

        columns = label_column + ["original_id"] + extra_columns + similarity_columns + list(
            map( lambda i: "word2vec_{0}".format( i ), range( 0, word2vec_provider.dimensions ) ) ) + list(
            map( lambda w: w + "_bow", self.wordlist ) )
        labels = []
        rows = []
        for idx in self.processed_data.index:
            current_row = []

            if not self.is_testing:
                # add label
                current_label = self.processed_data.loc[idx, "emotion"]
                labels.append( current_label )
                current_row.append( current_label )

            current_row.append( self.processed_data.loc[idx, "id"] )

            for _, col in enumerate( extra_columns ):
                current_row.append( self.processed_data.loc[idx, col] )

            # average similarities with words
            tokens = self.processed_data.loc[idx, "tokenized_text"]
            for main_word in map( lambda w: w.split( "_" )[0], similarity_columns ):
                current_similarities = [abs( sim ) for sim in
                                        map( lambda word: word2vec_provider.get_similarity( main_word, word.lower() ),
                                             tokens ) if
                                        sim is not None]
                if len( current_similarities ) <= 1:
                    current_row.append( 0 if len( current_similarities ) == 0 else current_similarities[0] )
                    continue
                max_sim = max( current_similarities )
                min_sim = min( current_similarities )
                current_similarities = [((sim - min_sim)/(max_sim - min_sim)) for sim in
                                        current_similarities]  # normalize to <0;1>
                current_row.append( np.array( current_similarities ).mean() )

            # add word2vec vector
            tokens = self.processed_data.loc[idx, "tokenized_text"]
            current_word2vec = []
            for _, word in enumerate( tokens ):
                vec = word2vec_provider.get_vector( word.lower() )
                if vec is not None:
                    current_word2vec.append( vec )

            averaged_word2vec = list( np.array( current_word2vec ).mean( axis=0 ) )
            current_row += averaged_word2vec

            # add bag-of-words
            tokens = set( self.processed_data.loc[idx, "text"] )
            for _, word in enumerate( self.wordlist ):
                current_row.append( 1 if word in tokens else 0 )

            rows.append( current_row )

        self.data_model = pd.DataFrame( rows, columns=columns )
        self.data_labels = pd.Series( labels )
        return self.data_model, self.data_labels

def log(text):
    print(text)
    with open("log.txt", "a") as log_file:
        log_file.write(str(text) + "\n")



if __name__ == "__main__":

    def main():

        for m in range( 3, 4 ):
            print("Preparing data with min_occurrences=" + str( m ))
            training_data, testing_data = preprare_data( m )
            log( "********************************************************" )
            log( "Validating for {0} min_occurrences:".format( m ) )
            # drop idx & id columns
            # if training_data.columns[0] == "idx":
            #     training_data = training_data.iloc[:, 1:]
            #
            # if testing_data.columns[0] == "idx":
            #     testing_data = testing_data.iloc[:, 1:]
            #
            # if "original_id" in training_data.columns:
            #     training_data.drop( "original_id", axis=1, inplace=True )
            #
            # if "original_id" in testing_data.columns:
            #     testing_data.drop( "original_id", axis=1, inplace=True )

            td = TwitterData()
            td.initialize( "data\\train.csv" )
            td.build_features()
            td.cleanup( TwitterCleanuper() )
            td.tokenize()
            td.stem()
            td.build_wordlist()
            td.build_final_model( word2vec )

            td.data_model.head( 5 )

        print("Done!")


    main()
