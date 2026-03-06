"""A script to analyse book data."""
import pandas as pd
import altair as alt

DATA_PATH = 'data/PROCESSED_DATA.csv'


def decade_pie(df: pd.DataFrame) -> alt.Chart:
    '''creates a pie chart showing the proportion of books released in each decade.'''
    df['decade'] = (df['year'] // 10) * 10
    chart = alt.Chart(df).mark_arc().encode(
        theta=alt.Theta(field="decade", type="nominal", aggregate="count"),
        color=alt.Color(field="decade", type="nominal")
    ).properties(
        title='Proportion of Books Released by Decade'
    )

    pie = chart.mark_arc(outerRadius=120)
    text = chart.mark_text(radius=140, size=20).encode(
        text=alt.Text("count():N"))

    return pie + text


def get_top_authors(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    '''Get the top N authors by total ratings.'''
    author_ratings = df.groupby('author_name')['ratings'].sum().reset_index()
    top_authors = author_ratings.sort_values(
        by='ratings', ascending=False).head(top_n)
    return top_authors


def most_rated_authors_bar(df: pd.DataFrame) -> alt.Chart:
    '''a sorted bar chart showing the total number of ratings for the ten most-rated authors.'''
    bar_chart = alt.Chart(get_top_authors(df)).mark_bar().encode(
        x=alt.X('ratings:Q', title='Total Ratings'),
        y=alt.Y('author_name:N', sort='-x', title='Author Name')
    ).properties(
        title='Top 10 Most-Rated Authors'
    )

    text = bar_chart.mark_text(dx=-40, dy=0, size=12).encode(
        text=alt.Text('ratings:Q', format=',')
    )
    bars = bar_chart.mark_bar().encode(
        x=alt.X('ratings:Q', title='Total Ratings'),
        y=alt.Y('author_name:N', sort='-x', title='Author Name')
    )
    return bars + text


def main() -> None:
    '''Main function to load data, create charts, and save them as PNG files.'''
    df = pd.read_csv(DATA_PATH)
    decade_chart = decade_pie(df)
    author_chart = most_rated_authors_bar(df)

    decade_chart.save('decade_releases.png')
    author_chart.save('top_authors.png')


if __name__ == '__main__':
    main()
