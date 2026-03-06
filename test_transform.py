import pandas as pd
import pytest

import process_raw_data as pr


def test_filter_known_authors():
    '''Test that only rows with known `author_id` are kept.'''
    df = pd.DataFrame({'author_id': [1, 2, 3], 'book_title': ['a', 'b', 'c']})
    author_db = pd.DataFrame({'id': [1, 3], 'name': ['X', 'Y']})
    out = pr.filter_known_authors(df, author_db)
    assert list(out['author_id']) == [1, 3]


def test_drop_nulls():
    '''Test that rows with null `author_id` or `book_title` are dropped.'''
    df = pd.DataFrame({
        'author_id': [1, None, 2],
        'book_title': ['Good', 'Bad', None]
    })
    out = pr.drop_nulls(df)
    # only the first row has both fields
    assert len(out) == 1
    assert out.iloc[0]['author_id'] == 1


def test_rename_and_select_columns():
    '''Test that columns are renamed and selected correctly.'''
    df = pd.DataFrame({
        'book_title': ['T'],
        'Year released': [2000],
        'Rating': ['4,5'],
        'ratings': ['100'],
        'name': ['Auth']
    })
    out = pr.rename_and_select_columns(df)
    assert list(out.columns) == [
        'title', 'author_name', 'year', 'rating', 'ratings']
    assert out.iloc[0]['title'] == 'T'


def test_clean_titles():
    '''Test that parenthetical text is removed from titles.'''
    df = pd.DataFrame({'title': ['My Book (Deluxe Edition)', 'Other']})
    out = pr.clean_titles(df)
    assert out.iloc[0]['title'] == 'My Book'
    assert out.iloc[1]['title'] == 'Other'


def test_normalize_numeric_columns_and_drop_invalid():
    '''Test that numeric columns are normalized and invalid rows are dropped.'''
    df = pd.DataFrame({
        'year': ['1999', 'not-a-year'],
        'rating': ['4,2', 'bad'],
        'ratings': ['1`00', 'x']
    })
    out = pr.normalize_numeric_columns(df)
    # only the first row should survive normalization
    assert len(out) == 1
    row = out.iloc[0]
    assert row['year'] == 1999
    assert pytest.approx(row['rating'], 0.01) == 4.2
    assert row['ratings'] == 100
    assert row['rating'] == 4.2


def test_sort_by_rating():
    '''Test that the DataFrame is sorted by rating in descending order.'''
    df = pd.DataFrame({'rating': [3.5, 4.9, 2.0], 'title': ['a', 'b', 'c']})
    out = pr.sort_by_rating(df)
    assert list(out['rating']) == [4.9, 3.5, 2.0]


def test_remove_duplicates():
    '''Test that duplicate rows are removed.'''
    df = pd.DataFrame({
        'title': ['Book A', 'Book B', 'Book A'],
        'author_name': ['Author X', 'Author Y', 'Author X'],
        'year': [2000, 2001, 2000],
        'rating': [4.5, 4.0, 4.5],
        'ratings': [100, 150, 100]
    })
    out = pr.remove_duplicates(df)
    # only the first and second rows are unique
    assert len(out) == 2
    assert list(out['title']) == ['Book A', 'Book B']
    assert list(out['author_name']) == ['Author X', 'Author Y']
    assert list(out['year']) == [2000, 2001]
    assert list(out['rating']) == [4.5, 4.0]
    assert list(out['ratings']) == [100, 150]


def test_remove_rating_outliers():
    '''Test that rows with ratings outside 0-5 are removed.'''
    df = pd.DataFrame({
        'title': ['Good Book', 'Bad Book', 'Weird Book'],
        'rating': [4.5, -1.0, 6.0]
    })
    out = pr.remove_rating_outliers(df)
    # only the first row has a valid rating
    assert len(out) == 1
    assert out.iloc[0]['title'] == 'Good Book'
    assert out.iloc[0]['rating'] == 4.5


def test_remove_year_outliers():
    '''Test that rows with years outside 1500-current year are removed.'''
    current_year = pd.Timestamp.now().year
    df = pd.DataFrame({
        'title': ['Old Book', 'Future Book', 'Normal Book'],
        'year': [1499, current_year + 1, 2000]
    })
    out = pr.remove_year_outliers(df)
    # only the third row has a valid year
    assert len(out) == 1
    assert out.iloc[0]['title'] == 'Normal Book'
    assert out.iloc[0]['year'] == 2000
