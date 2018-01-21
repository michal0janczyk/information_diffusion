import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
import matplotlib.pyplot as plt

data = pd.read_csv('Data/customer_review.csv')
data.head(5)

SIA = SentimentIntensityAnalyzer()

data['polarity_score']=data.Review.apply(lambda x:SIA.polarity_scores(x)['compound'])
data['neutral_score']=data.Review.apply(lambda x:SIA.polarity_scores(x)['neu'])
data['negative_score']=data.Review.apply(lambda x:SIA.polarity_scores(x)['neg'])
data['positive_score']=data.Review.apply(lambda x:SIA.polarity_scores(x)['pos'])
data['sentiment']=''
data.loc[data.polarity_score>0,'sentiment']='POSITIVE'
data.loc[data.polarity_score==0,'sentiment']='NEUTRAL'
data.loc[data.polarity_score<0,'sentiment']='NEGATIVE'
print data.head()

data.sentiment.value_counts().plot(kind='bar',title="sentiment analysis")
plt.show()