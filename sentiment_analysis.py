# -*- coding: utf-8 -*-
"""Sentiment Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bm-ew970KDq8McPCIIEqGGkOxavonAAC

# Importing relevant libraries
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
import string
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import missingno as msno
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import warnings
import pickle
warnings.filterwarnings("ignore")
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

"""# Loading the data"""

df = pd.read_csv('movie_review.csv')

df.head(20)

df.shape

"""# Data preprocessing and cleaning

## Dropping irrelevant columns
"""

df = df.drop(columns=['fold_id','cv_tag','html_id','sent_id'])
df.info()

"""## Displaying some reviews of both classes"""

positive_reviews = df[df['tag'] == 'pos']
negative_reviews = df[df['tag'] == 'neg']

"""### Showing positive reviews"""

for i in range (15):
  print(f"Review no:{i+1}\n{positive_reviews['text'].iloc[i]}")
  print("\n")

"""### Showing negative reviews"""

for i in range (15):
  print(f"Review no:{i+1}\n{negative_reviews['text'].iloc[i]}")
  print("\n")

"""## Checking for null values"""

msno.bar(df)

"""*No feature has missing values*

### Dropping reviews that has empty white space values
"""

blanks = []
for i,twt,lb in df.itertuples():
  if type(twt) == str:
    if twt.isspace():
      blanks.append(i)

df.drop(blanks,inplace=True)

df.shape

"""*No such empty white spaces found*

## Check for class imbalance
"""

class_count = df['tag'].value_counts()
plt.figure(figsize=(8, 6))
ax = sns.barplot(x=class_count.index, y=class_count)
plt.xlabel('Class', fontsize=18)
plt.ylabel('Count', fontsize=18)

# Add count labels to the bars
for p in ax.patches:
    count = int(p.get_height())  # Convert the count to integer
    ax.annotate(f"{count}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center',
                xytext=(0, 5), textcoords='offset points')

plt.show()

"""*Data is almost balanced*

## Data cleaning
"""

def clean_text(sentence):
    # Lowercase the text
    sentence = sentence.lower()

    # Remove special characters
    sentence = re.sub(r"[^\w\s]", "", sentence)

    # Remove punctuation
    sentence = sentence.translate(str.maketrans("", "", string.punctuation))

    # Remove numbers
    sentence = re.sub(r"\d+", "", sentence)

    # Remove HTML tags
    sentence = BeautifulSoup(sentence, "html.parser").get_text()

    # Remove URLs
    sentence = re.sub(r"http\S+|www\S+|https\S+", "", sentence)

    # Remove whitespace
    sentence = re.sub(r"\s+", " ", sentence).strip()

    # Tokenize the sentence
    tokens = word_tokenize(sentence)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    filtered_tokens = [token for token in tokens if token not in stop_words]

    # Perform stemming
    lemmatizer = WordNetLemmatizer()
    lemmatised = [lemmatizer.lemmatize(i) for i in filtered_tokens]

    cleaned_sentence = " ".join(lemmatised)

    return cleaned_sentence

"""### Showing some positve reviews after transformation"""

positive_reviews['text'] = positive_reviews['text'].apply(lambda x : clean_text(x))
for i in range (15):
  print(f"Review no:{i+1}\n{positive_reviews['text'].iloc[i]}")
  print("\n")

"""### Showing some negative reviews after transformation"""

negative_reviews['text'] = negative_reviews['text'].apply(lambda x : clean_text(x))
for i in range (15):
  print(f"Review no:{i+1}\n{negative_reviews['text'].iloc[i]}")
  print("\n")

df['text'] = df['text'].apply(lambda x : clean_text(x))

"""## Generating word cloud of most frequent words of each class"""

max_words = 50
positive_wordcloud = WordCloud(width=800, height=400,max_words=max_words,background_color ='white').generate(' '.join(positive_reviews['text']))
negative_wordcloud = WordCloud(width=800, height=400,max_words=max_words).generate(' '.join(negative_reviews['text']))


plt.figure(figsize=(12,6))
plt.subplot(1, 2, 1)
plt.imshow(positive_wordcloud, interpolation='bilinear')
plt.title('Positive Reviews',fontsize = 10)
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(negative_wordcloud, interpolation='bilinear')
plt.title('Negative Reviews',fontsize = 10)
plt.axis('off')


plt.show()

"""# Model development

## Declaring Inputs & Targets variable
"""

x = df["text"]
y = df["tag"]

"""## Splitting the data"""

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2,random_state=42)

"""## Converting text to matrix of TFIDF features"""

vectorizer = TfidfVectorizer()
x_train = vectorizer.fit_transform(x_train)
x_test = vectorizer.transform(x_test)

"""## Logistic Regression"""

LR = LogisticRegression(max_iter=500)
LR.fit(x_train,y_train)

"""### Prediction on test data"""

pred_lr=LR.predict(x_test)

"""### Model evaluation"""

LR.score(x_test, y_test)

print(classification_report(y_test,pred_lr))

"""# Manual Testing"""

def manual_testing(Review):
  Review = vectorizer.transform([clean_text(Review)]).toarray()
  print(LR.predict(Review))

manual_testing("Script is truly genius. Its not like most other bollywood movies filled with item songs. This is different and sits among top Indian films of all time.Very much recommended.")