import sys
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


lemmatizer = WordNetLemmatizer()


def analyze_text(text):
    sia = SentimentIntensityAnalyzer()
    text = str(text)
    score = sia.polarity_scores(text)
    return score['compound']

def clean_tokens(tokens):
    stop_words = set(stopwords.words('english'))

    # Add any additional stop words
    custom_stop_words = ['said', 'also', 'us', 'one', 'u', 'get', 'year', 'could', 'even','like', 'two', 'say', 'week'
                         'still','told', 'since','well', 'thats', 'since', 'way', 'many', 'told', 'last', 'first', 'much', 
                         'april', 'take', 'three', 'however', 'make']
    stop_words.update(custom_stop_words)

    return [lemmatizer.lemmatize(word.lower()) for word in tokens if word.lower() not in stop_words and word.isalpha()]

def tokenize_text(text):
    # Ensure text is a string
    text = str(text).lower()  # Convert to lowercase to standardize
    stop_words = set(stopwords.words('english'))
    
    # Tokenize text
    words = word_tokenize(text)
    
    # Remove stopwords and non-alphabetic characters
    filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
    
    return filtered_words

def pos_tagging(text):
    # Tokenize and apply POS tagging
    words = word_tokenize(text)
    return pos_tag(words)

def named_entity_recognition(text):
    # Tokenize
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
    df['tokens'] = df['tokens'].apply(clean_tokens)

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
