import streamlit as st
import plotly.express as px
import pandas as pd
import ast

# Example data
news = pd.read_csv('Output/news_tokens.csv')


today = pd.Timestamp.now().normalize()
todays_news = news[news['collection_date'] == today]

if todays_news.empty:
    yesterday = today - pd.Timedelta(days=1)
    todays_news = news[news['collection_date'] == yesterday]

    # Display a message if reverting to the previous day
    print("No news for today. Showing yesterday's data.")

# Safely convert stringified lists to actual lists
news['tokens'] = news['tokens'].apply(ast.literal_eval)

# Explode the 'tokens' list into separate rows
news_long = news.explode('tokens')

# Group by 'tokens' and calculate the average sentiment, ignoring NaN values
average_sentiment = news_long.groupby('tokens', as_index=False).agg(avg_sentiment=('sentiment', 'mean'))

# Display the DataFrame
print(average_sentiment)

# Optionally, filter out any specific unwanted tokens (e.g., 'nan' or 'new' if they are irrelevant)
news_long = news_long[~news_long['tokens'].isin(['nan', 'new', 'would'])]

# Count occurrences and sort them
token_counts = news_long['tokens'].value_counts().reset_index()
token_counts.columns = ['tokens', 'count']
token_counts = token_counts.sort_values(by='count', ascending=False)


# Assuming token_counts and average_sentiment are already loaded DataFrames with appropriate columns
# Joining the datasets on the 'tokens' column
token_data = pd.merge(token_counts, average_sentiment, on='tokens')

# Filtering for the top 25 most frequent tokens and sorting
top_tokens = token_data.nlargest(25, 'count').sort_values(by='count', ascending=False)

# Creating a Plotly Express figure
bar_fig = px.bar(top_tokens, x="count", y="tokens", orientation='h', color="avg_sentiment",
             color_continuous_scale=px.colors.sequential.Viridis, title="Token Sentiment Analysis")

# Display the figures
bar_fig.show()

# Using tabs
tab1, tab2 = st.tabs(["Bar Chart", "Data Table"])


st.markdown("# Main page 🎈")
st.sidebar.success("Select a page above.")

with tab1:
    st.header("Bottom sentiment words")
    st.plotly_chart(bar_fig, use_container_width=True)

with tab2:
    st.header("This is the data table tab")
    st.plotly_chart(bar_fig, use_container_width=True)