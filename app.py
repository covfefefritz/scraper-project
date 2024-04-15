import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
import ast
from streamlit_gsheets import GSheetsConnection



def load_data(news):
    news['collection_date'] = pd.to_datetime(news['collection_date'], format='%Y-%m-%d', errors='coerce')
    
    # Check for rows where 'collection_date' could not be parsed and drop them
    if news['collection_date'].isnull().any():
        print(f"Dropping {news['collection_date'].isnull().sum()} rows where 'collection_date' could not be parsed.")
        news = news.dropna(subset=['collection_date'])
    
    news['collection_date'] = news['collection_date'].dt.date
    return news

def preprocess_data(news, unwanted_tokens):
    news['tokens'] = news['tokens'].apply(ast.literal_eval)
    news = news[~news['tokens'].isin(unwanted_tokens)]
    return news

def filter_data_by_date(news_long, reference_date):
    filtered_news = news_long[news_long['collection_date'] == reference_date]
    if filtered_news.empty:
        reference_date -= pd.Timedelta(days=1)
        filtered_news = news_long[news_long['collection_date'] == reference_date]
        print(f"No news for the requested date. Showing data for {reference_date}.")
    return filtered_news

def create_plot(data, x, y, title, orientation='h', plot_type='bar', color='avg_sentiment', color_scale='Viridis'):
    """
    Parameters:
        data (DataFrame): The data to plot.
        x (str): The name of the column for the x-axis.
        y (str): The name of the column for the y-axis.
        title (str): The title of the plot.
        orientation (str): The orientation of the bars ('v' for vertical, 'h' for horizontal).
        plot_type (str): Type of the plot ('bar', 'line', etc.).
        color (str): The name of the column based on which to apply color scaling.
        color_scale (str): The color scale to use.
    Returns:
        Figure: A Plotly Express figure.
    """
    if plot_type == 'bar':
        fig = px.bar(data, x=x, y=y, orientation=orientation, color=color,
                     color_continuous_scale=px.colors.sequential.__dict__[color_scale], title=title)
    elif plot_type == 'line':
        fig = px.line(data, x=x, y=y, color=color, title=title)
    # Add more plot types when needed
    return fig

def setup_bar_chart_df(df):
    token_counts = df['tokens'].value_counts().reset_index()
    token_counts.columns = ['tokens', 'count']
    token_counts = token_counts.sort_values(by='count', ascending=False)

    # Joining the datasets on the 'tokens' column
    average_sentiment = news_long.groupby('tokens', as_index=False).agg(avg_sentiment=('sentiment', 'mean'))
    token_data = pd.merge(token_counts, average_sentiment, on='tokens')

    # Filtering for the top 25 most frequent tokens and sorting
    top_tokens = token_data.nlargest(25, 'count').sort_values(by='count', ascending=False)
    return top_tokens

def setup_sentiment_over_time(df):
    top_tokens = df['tokens'].value_counts().nlargest(100).index
    # Filter the dataset to include only the top tokens
    df_top = df[df['tokens'].isin(top_tokens)]
    df_avg = df_top.groupby(['collection_date', 'tokens']).sentiment.mean().reset_index()
    return df_avg
  
def setup_occurrence_over_time(df):
    top_tokens = df['tokens'].value_counts().nlargest(100).index
    # Filter the dataset to include only the top tokens
    df_top = df[df['tokens'].isin(top_tokens)]
    df_occurrences = df_top.groupby(['collection_date', 'tokens']).size().reset_index(name='counts')
    return df_occurrences

## main 
conn = st.connection("gsheets", type=GSheetsConnection)
news = conn.read()

news = load_data(news)
news = preprocess_data(news, ['nan', 'new', 'would'])

# Explode the list of words into separate rows
news_long = news.explode('tokens')

reference_date = st.sidebar.date_input("Select Date", datetime.now().date())
news_by_date = filter_data_by_date(news_long, reference_date)

top_tokens_by_date = setup_bar_chart_df(news_by_date)
top_tokens_all_time = setup_bar_chart_df(news_long)
avg_token_sentiment_over_time = setup_sentiment_over_time(news_long)
token_occurrence_over_time = setup_occurrence_over_time(news_long)

# Create plots
all_time_chart = create_plot(top_tokens_all_time, x='count', y='tokens', title="Token Sentiment Analysis (All Time)",
                             color_scale='Viridis')

selected_day_chart = create_plot(top_tokens_by_date, x='count', y='tokens', title=f"Token Sentiment Analysis ({reference_date})",
                                 color_scale='Viridis')


# Using tabs
tab1, tab2, tab3, tab4 = st.tabs(["All time data", "Selected Date Data", "Word sentiment over time", "Word occurrence over time"])

st.markdown("# Python and data analysis practice page 🎈 \n Currently scraping financial news off zerohedge and CNBC and experimenting with the results \n \n Link to the repo: https://github.com/covfefefritz/scraper-project")

with tab1:
    st.header("Top Occurring Words and Their Sentiment Score (All Time)")
    st.plotly_chart(all_time_chart, use_container_width=True)

with tab2:
    st.header(f"Top Occurring Words and Their Sentiment Scores ({reference_date})")
    st.plotly_chart(selected_day_chart, use_container_width=True)

with tab3: 
    st.header(f"Specific word sentiment score over time")
    selected_tokens = st.multiselect(
    'Select tokens to visualize:',
    options=news_long['tokens'].unique(),  # Unique tokens from the dataset
    default=['biden', 'rate', 'gold'])  # Default selection
    df_filtered = avg_token_sentiment_over_time[avg_token_sentiment_over_time['tokens'].isin(selected_tokens)]
    sentiment_over_time_chart = create_plot(df_filtered, x='collection_date', y='sentiment', color='tokens', color_scale='Viridis', title='Sentiment Score over time', plot_type='line')
    st.plotly_chart(sentiment_over_time_chart, use_container_width=True)

with tab4: 
    st.header(f"Specific word occurence over time")
    selected_tokens = st.multiselect(
    'Select tokens to visualize:',
    options=news_long['tokens'].unique(),  # Unique tokens from the dataset
    default=['biden', 'rate', 'gold', 'russia'])  # Default selection
    df_filtered = token_occurrence_over_time[token_occurrence_over_time['tokens'].isin(selected_tokens)]
    occurrence_over_time_chart = create_plot(df_filtered, x='collection_date', y='counts', color='tokens', color_scale='Viridis', title='Sentiment Score over time', plot_type='line')
    st.plotly_chart(occurrence_over_time_chart, use_container_width=True)
