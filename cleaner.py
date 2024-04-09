import sys
import pandas as pd
import re
from bs4 import BeautifulSoup
from datetime import date



def clean_text(text):
    # Remove HTML entities and tags with Beautiful Soup
    soup = BeautifulSoup(text, "lxml")
    text = soup.get_text(separator=" ")
    
    # Extra removal of residual HTML tags
    #text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities
    text = re.sub(r'&[a-zA-Z]+;', '', text)

    # Convert to lowercase, remove numbers, and punctuation
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    return text

def clean_data(file_path):
    # Load the dataset
    df = pd.read_csv(file_path)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    df['article_text'] = df['article_text'].astype(str)

    # Handling missing values
    today = date.today()
    df['article_text'].fillna('No content', inplace=True)
    df['collection_date'].fillna(today, inplace=True)

    # Normalize text
    df['article_text'] = df['article_text'].apply(clean_text)

    # Save the cleaned data
    cleaned_file_path = file_path.replace('raw/news', 'cleaned/news')
    df.to_csv(cleaned_file_path, index=False)
    print(f"Cleaned data saved to {cleaned_file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cleaner.py <filename>")
        sys.exit(1)
    
    # Assuming the script and the Output folder are in the same directory
    file_path = sys.argv[1]
    clean_data(file_path)
