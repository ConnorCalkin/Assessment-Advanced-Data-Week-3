import pandas as pd
import analyse_processed_data as ap


def test_get_top_authors():
    '''Test that the top authors are correctly identified by total ratings.'''
    df = pd.DataFrame({
        'author_name': ['A', 'B', 'C'],
        'ratings': [100, 200, 150]
    })
    out = ap.get_top_authors(df, top_n=2)
    assert len(out) == 2
    assert list(out['author_name']) == ['B', 'C']
    assert list(out['ratings']) == [200, 150]
