
import altair as alt
import pandas as pd
from stop_words import get_stop_words

DATA_PATH = 'data/PROCESSED_DATA.csv'


def load_data():
    '''Load the processed data from CSV.'''
    return pd.read_csv(DATA_PATH)


def get_word_counts_in_titles(df: pd.DataFrame) -> pd.DataFrame:
    '''Extract the most frequent words in book titles.'''
    # Split titles into words and explode into a long format
    words = df['title'].str.split().explode()
    # Count the frequency of each word
    word_counts = words.value_counts().reset_index()
    word_counts.columns = ['word', 'count']
    return word_counts


def filter_stop_words(df: pd.DataFrame, stop_words: set) -> pd.DataFrame:
    '''Filter out common stop words from the word counts.'''
    return df[~df['word'].str.lower().isin(stop_words)]


def get_top_keywords(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    '''
    Get the top N keywords from the word counts.
    Key words are determined by filtering out stop words
    '''
    word_counts = get_word_counts_in_titles(df)
    stop_words = get_stop_words('english')
    stop_words.append('&')  # add '&' to stop words since it's common in titles
    key_word_counts = filter_stop_words(
        word_counts, stop_words=stop_words)
    top_key_words = key_word_counts.sort_values(
        by='count', ascending=False).head(top_n)
    return top_key_words


def create_bar_chart(df: pd.DataFrame) -> alt.Chart:
    '''Create a bar chart of the top keywords.'''
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('count:Q', title='Count'),
        y=alt.Y('word:N', sort='-x', title='Keyword')
    ).properties(
        title='Top Keywords in Book Titles'
    )
    return chart


if __name__ == '__main__':
    data_df = load_data()
    top_key_words = get_top_keywords(data_df, 20)
    bar_chart = create_bar_chart(top_key_words)
    bar_chart.save('top_keywords.png')
