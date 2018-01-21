import gensim

# Load Google's pre-trained Word2Vec model.
model = gensim.models.Word2Vec.load_word2vec_format('Data/GoogleNews-vectors-negative300.bin', binary=True)

model.most_similar(positive=['woman', 'king'], negative=['man'], topn=5)
model.most_similar(['girl', 'father'], ['boy'], topn=3)
model.doesnt_match("breakfast cereal dinner lunch".split())

sentences = [['cigarette','smoking','is','injurious', 'to', 'health'],['cigarette','smoking','causes','cancer'],['cigarette','are','not','to','be','sold','to','kids']]


# train word2vec on the two sentences
model = gensim.models.Word2Vec(sentences, min_count=1, sg=1, window = 3)

model.most_similar(positive=['cigarette', 'smoking'], negative=['kids'], topn=1)


# class Word2VecProvider(object):
#     word2vec = None
#
#     dimensions = 0
#
#     def load(self, path_to_word2vec):
#         self.word2vec = gensim.models.Word2Vec.load_word2vec_format(path_to_word2vec, binary=False)
#         self.word2vec.init_sims(replace=True)
#         self.dimensions = self.word2vec.vector_size
#
#     def get_vector(self, word):
#         if word not in self.word2vec.vocab:
#             return None
#
#         return self.word2vec.syn0norm[self.word2vec.vocab[word].index]
#
#     def get_similarity(self, word1, word2):
#         if word1 not in self.word2vec.vocab or word2 not in self.word2vec.vocab:
#             return None
#
#         return self.word2vec.similarity(word1, word2)
