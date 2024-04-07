import sys
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
from nltk.corpus import stopwords
import nltk


def analyze_text(text):
    sia = SentimentIntensityAnalyzer()
    text = str(text)
    score = sia.polarity_scores(text)
    return score['compound']

def tokenize_text(text):
    # Tokenize and remove stopwords
    text = str(text)
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    return [word for word in words if word not in stop_words]

def pos_tagging(text):
    # Tokenize and apply POS tagging
    words = word_tokenize(text)
    return pos_tag(words)

def named_entity_recognition(text):
    # Tokenize, POS tag, and perform NER
    words = word_tokenize(text)
    tags = pos_tag(words)
    tree = ne_chunk(tags)
    
    return [f"{ent.label()}:{' '.join(c[0] for c in ent)}" for ent in tree if isinstance(ent, Tree)]

def analyze_data(file_path):
    df = pd.read_csv(file_path)

    # Sentiment analysis
    df['sentiment'] = df['article_text'].apply(analyze_text)

    # May need to expliore this further
    df['tokens'] = df['article_text'].apply(tokenize_text)

    # Drop the article_text column to get a cleaner result file
    df.drop(columns=['article_text'], inplace=True)

    # Save the analyzed data
    analyzed_file_path = file_path.replace('cleaned/news', 'analyzed/news')
    df.to_csv(analyzed_file_path, index=False)
    print(f"Analyzed data saved to {analyzed_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <filename>")
        sys.exit(1)

    file_path = sys.argv[1]
    analyze_data(file_path)
