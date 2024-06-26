# -*- coding: utf-8 -*-
"""app.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KDi5DTS4zDdWUCEp5xuYdEI0y7lNRHpv
"""

import streamlit as st
import joblib
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from googletrans import Translator
from langdetect import detect
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load necessary NLTK data
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('vader_lexicon')

# Load the model and vectorizer
nb_model = joblib.load('naive_bayes_model(2).pkl')
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Text preprocessing functions
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"\b(n't)\b", ' not', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)

def predict_sentiment(text):
    text_processed = preprocess_text(text)
    text_vectorized = tfidf_vectorizer.transform([text_processed])
    prediction = nb_model.predict(text_vectorized)
    return prediction[0]

# Streamlit UI
st.title("Advanced Sentiment Analysis Web App")

st.sidebar.header("Options")
user_input = st.sidebar.text_area("Enter a review to predict its sentiment:", height=200, key='user_input')

if st.sidebar.button("Predict Sentiment"):
    sentiment = predict_sentiment(user_input)
    st.sidebar.write(f"Predicted sentiment: {sentiment}")

st.write("## Analyze Reviews from CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### Uploaded Data")
    st.write(df.head())

    if 'review' in df.columns:
        translator = Translator()
        df['review_translated'] = df['review'].apply(lambda x: translator.translate(x, dest='en').text if detect(x) != 'en' else x)

        df['review_processed'] = df['review_translated'].apply(preprocess_text)
        df['predicted_sentiment'] = df['review_processed'].apply(predict_sentiment)

        st.write("### Sentiment Analysis Results")
        st.write(df[['review', 'review_translated', 'predicted_sentiment']])

        st.write("### Sentiment Distribution")
        sentiment_counts = df['predicted_sentiment'].value_counts()
        st.bar_chart(sentiment_counts)
    else:
        st.write("Error: The uploaded CSV file does not contain a 'review' column.")

if st.checkbox("Show raw data"):
    st.write(df)