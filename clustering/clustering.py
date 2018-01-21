from __future__ import print_function

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np

newsgroups_train = fetch_20newsgroups( subset='train' )
print(list( newsgroups_train.target_names ))

categories = ['alt.atheism', 'comp.graphics', 'rec.motorcycles']

dataset = fetch_20newsgroups( subset='all', categories=categories, shuffle=True, random_state=2017 )

print("%d documents"%len( dataset.data ))
print("%d categories"%len( dataset.target_names ))

labels = dataset.target

print("Extracting features from the dataset using a sparse vectorizer")
vectorizer = TfidfVectorizer( stop_words='english' )
X = vectorizer.fit_transform( dataset.data )

print("n_samples: %d, n_features: %d"%X.shape)

from sklearn.decomposition import TruncatedSVD

# Lets reduce the dimensionality to 2000
svd = TruncatedSVD( 2000 )
lsa = make_pipeline( svd, Normalizer( copy=False ) )

X = lsa.fit_transform( X )

explained_variance = svd.explained_variance_ratio_.sum()
print("Explained variance of the SVD step: {}%".format( int( explained_variance*100 ) ))

km = KMeans( n_clusters=3, init='k-means++', max_iter=100, n_init=1 )

# Scikit learn provides MiniBatchKMeans to run k-means in batch mode suitable for a very large corpus
# km = MiniBatchKMeans(n_clusters=5, init='k-means++', n_init=1, init_size=1000, batch_size=1000)

print( "Clustering sparse data with %s"%km )
km.fit( X )

print( "Top terms per cluster:" )
original_space_centroids = svd.inverse_transform( km.cluster_centers_ )
order_centroids = original_space_centroids.argsort()[:, ::-1]

terms = vectorizer.get_feature_names()
for i in range( 3 ):
    print( "Cluster %d:"%i, end='' )
    for ind in order_centroids[i, :10]:
        print( ' %s'%terms[ind], end='' )
    print()

from sklearn.metrics.pairwise import cosine_similarity

dist = 1 - cosine_similarity( X )

from scipy.cluster.hierarchy import ward, dendrogram

linkage_matrix = ward( dist )  # define the linkage_matrix using ward clustering pre-computed distances

fig, ax = plt.subplots( figsize=(8, 8) )  # set size
ax = dendrogram( linkage_matrix, orientation="right" )

plt.tick_params( axis='x', which='both', bottom='off', top='off', labelbottom='off' )

plt.tight_layout()  # show plot with tight layout
plt.show()
