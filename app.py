import streamlit as st
import plotly.express as px
import pandas as pd
import ast

# Example data
news = pd.read_csv('Output/news_tokens.csv')
today = pd.Timestamp.now().normalize()
news['tokens'] = news['tokens'].apply(ast.literal_eval)

# Explode the list of words into separate rows
news_long = news.explode('tokens')

todays_news = news_long[news_long['collection_date'] == today]
if todays_news.empty:
    yesterday = today - pd.Timedelta(days=1)
    todays_news = news[news['collection_date'] == yesterday]

    # Display a message if reverting to the previous day
    print("No news for today. Showing yesterday's data.")


# Group by 'tokens' and calculate the average sentiment, ignoring NaN values
average_sentiment = news_long.groupby('tokens', as_index=False).agg(avg_sentiment=('sentiment', 'mean'))
todays_news_sentiment = todays_news.groupby('tokens', as_index=False).agg(avg_sentiment=('sentiment', 'mean'))

# Filter out any specific unwanted tokens, 
news_long = news_long[~news_long['tokens'].isin(['nan', 'new', 'would'])]
todays_news = todays_news[~todays_news['tokens'].isin(['nan', 'new', 'would'])]

# Count occurrences and sort them
token_counts = news_long['tokens'].value_counts().reset_index()
token_counts.columns = ['tokens', 'count']
token_counts = token_counts.sort_values(by='count', ascending=False)

token_counts_today = todays_news['tokens'].value_counts().reset_index()
token_counts_today.columns = ['tokens', 'count']
token_counts_today = token_counts_today.sort_values(by='count', ascending=False)


# Assuming token_counts and average_sentiment are already loaded DataFrames with appropriate columns
# Joining the datasets on the 'tokens' column
token_data = pd.merge(token_counts, average_sentiment, on='tokens')
token_data_today = pd.merge(token_counts_today, todays_news_sentiment, on='tokens')
# Filtering for the top 25 most frequent tokens and sorting
top_tokens = token_data.nlargest(25, 'count').sort_values(by='count', ascending=False)
top_tokens_today = token_data_today.nlargest(25, 'count').sort_values(by='count', ascending=False)
# Creating a Plotly Express figure
bar_fig = px.bar(top_tokens, x="count", y="tokens", orientation='h', color="avg_sentiment",
             color_continuous_scale=px.colors.sequential.Viridis, title="Token Sentiment Analysis")

bar_fig_today = px.bar(top_tokens_today, x="count", y="tokens", orientation='h', color="avg_sentiment",
             color_continuous_scale=px.colors.sequential.Viridis, title="Token Sentiment Analysis")
# Display the figures
bar_fig.show()
bar_fig_today.show()

# Using tabs
tab1, tab2 = st.tabs(["Bar Chart", "Data Table"])


st.markdown("# Python and data analysis practice page 🎈 \n Currently scraping financial news off zerohedge and CNBC and experimenting with the results")
st.sidebar.success("Select a page above.")

with tab1:
    st.header("Top occuring words and their sentiment score since start")
    st.plotly_chart(bar_fig, use_container_width=True)

with tab2:
    st.header("Latest day top occuring words")
    st.plotly_chart(bar_fig_today, use_container_width=True)