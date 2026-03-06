import get_keywords as gk
import pandas as pd


def test_get_word_counts_in_titles():
    '''Test that word counts are correctly extracted from titles.'''
    df = pd.DataFrame({'title': ['The Great Gatsby', 'Great Expectations']})
    out = gk.get_word_counts_in_titles(df)
    expected_counts = {'The': 1, 'Great': 2, 'Gatsby': 1, 'Expectations': 1}
    for _, row in out.iterrows():
        assert row['count'] == expected_counts[row['word']]


def test_filter_stop_words():
    '''Test that stop words are correctly filtered out.'''
    df = pd.DataFrame({'word': ['The', 'Great', 'and'], 'count': [1, 2, 3]})
    stop_words = {'the', 'and'}
    out = gk.filter_stop_words(df, stop_words)
    assert list(out['word']) == ['Great']
    assert list(out['count']) == [2]


def test_get_top_keywords_gets_top_keyword():
    '''
        Test that the top keywords are correctly identified.
        We use zoom instead of great to avoid stop word filtering.
    '''
    df = pd.DataFrame({'title': ['The Zoom Gatsby', 'Zoom Expectations']})
    out = gk.get_top_keywords(df, top_n=1)
    assert len(out) == 1
    assert out.iloc[0]['word'] == 'Zoom'
    assert out.iloc[0]['count'] == 2


def test_get_top_keywords_filters_stop_words():
    '''
        Test that stop words are filtered out in get_top_keywords.
        We use zoom instead of great to avoid stop word filtering.
    '''
    df = pd.DataFrame({'title': ['The Zoom Gatsby', 'Zoom Expectations']})
    out = gk.get_top_keywords(df, top_n=10)
    assert 'The' not in out['word'].values
    assert 'and' not in out['word'].values
    assert 'Zoom' in out['word'].values
