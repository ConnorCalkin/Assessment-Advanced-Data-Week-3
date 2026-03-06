"""A script to process book data."""
import argparse
import sqlite3
import logging

import pandas as pd
from datetime import datetime


AUTHOR_PATH = 'data/authors.db'

# create logging
logging.basicConfig(level=logging.DEBUG)


def get_args() -> argparse.Namespace:
    """Parse command-line arguments and return the namespace."""
    parser = argparse.ArgumentParser(description='Process book data.')
    parser.add_argument('file_path', type=str,
                        help='The path to the raw data file.')
    return parser.parse_args()


def load_csv(file_path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(file_path)


def load_author_db(file_path: str) -> pd.DataFrame:
    """Load the `author` table from a SQLite database into a DataFrame.

    Ensures the result has `id` and `name` columns when possible.
    """
    con = sqlite3.connect(file_path)
    cur = con.cursor()
    cur.execute("SELECT * FROM author")
    df = pd.DataFrame(cur.fetchall(), columns=['id', 'name'])
    con.close()
    return df


def filter_known_authors(df: pd.DataFrame, author_db: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows whose `author_id` exists in `author_db`.`"""
    mask = df['author_id'].isin(author_db['id'])
    unknown_authors = df[~mask]
    if not unknown_authors.empty:
        logging.debug(
            f"Dropped rows with unknown authors:\n{unknown_authors}")
    return df[mask]


def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
        Drop rows missing `author_id` or `book_title`.
        Logs all dropped rows at the DEBUG level for traceability.
    """
    mask = df['author_id'].isna() | df['book_title'].isna()
    dropped_rows = df[mask]
    if not dropped_rows.empty:
        logging.debug(f"Dropped rows due to missing values:\n{dropped_rows}")

    return df[~mask]


def merge_author_names(df: pd.DataFrame, author_db: pd.DataFrame) -> pd.DataFrame:
    """Merge author names into the dataset as `name` (later renamed)."""
    return df.merge(author_db[['id', 'name']], left_on='author_id', right_on='id', how='left')


def rename_and_select_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw columns to canonical names and select output columns."""
    column_mapping = {
        'book_title': 'title',
        'Year released': 'year',
        'Rating': 'rating',
        'ratings': 'ratings',
        'name': 'author_name'
    }
    df = df.rename(columns=column_mapping)
    return df[['title', 'author_name', 'year', 'rating', 'ratings']]


def clean_titles(df: pd.DataFrame) -> pd.DataFrame:
    """Remove any parenthetical text from `title` values."""
    out = df.copy()
    out['title'] = out['title'].str.replace(r'\s*\(.*\)\s*', '', regex=True)
    return out


def normalize_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and convert `year`, `rating`, and `ratings` to numeric types.

    - Replace comma decimal separators in `rating` with periods.
    - Remove stray backticks from `ratings`.
    - Coerce invalid values and drop rows with missing numeric values.
    """
    out = df.copy()
    out['rating'] = out['rating'].astype(
        str).str.replace(',', '.', regex=False)
    out['year'] = pd.to_numeric(out['year'], errors='coerce')
    out['rating'] = pd.to_numeric(out['rating'], errors='coerce')
    out['ratings'] = out['ratings'].astype(
        str).str.replace("`", '', regex=False)
    out['ratings'] = pd.to_numeric(out['ratings'], errors='coerce')

    mask = out['year'].isna() | out['rating'].isna() | out['ratings'].isna()
    dropped_rows = out[mask]
    if not dropped_rows.empty:
        logging.debug(
            f"Dropped rows due to invalid numeric values:\n{dropped_rows}")
    return out[~mask]


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
        Remove duplicate rows.
        Only assumes duplicate rows are identical across all columns, 
            so it keeps the first occurrence.
    """
    mask = df.duplicated()
    duplicate_rows = df[mask]
    if not duplicate_rows.empty:
        logging.debug(f"Found duplicate rows:\n{duplicate_rows}")
    return df[~mask]


def remove_rating_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with `rating` outside the range 0-5."""
    mask = (df['rating'] < 0) | (df['rating'] > 5)
    outliers = df[mask]
    if not outliers.empty:
        logging.debug(f"Found rating outliers:\n{outliers}")
    return df[~mask]


def remove_year_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with `year` outside the range 1500-current year."""
    current_year = datetime.now().year
    mask = (df['year'] < 1500) | (df['year'] > current_year)
    outliers = df[mask]
    if not outliers.empty:
        logging.debug(f"Found year outliers:\n{outliers}")
    return df[~mask]


def sort_by_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Return the DataFrame sorted by `rating` in descending order."""
    return df.sort_values(by='rating', ascending=False)


def export_as_csv(df: pd.DataFrame, file_path: str) -> None:
    """Export the DataFrame to CSV, overwriting if the file exists."""
    df.to_csv(file_path, index=False)


def main() -> None:
    """Main orchestration: load inputs, apply transformations, and export."""
    args = get_args()
    file_path = args.file_path

    unclean_data = load_csv(file_path)
    author_db = load_author_db(AUTHOR_PATH)

    clean_data = filter_known_authors(unclean_data, author_db)
    clean_data = drop_nulls(clean_data)
    clean_data = merge_author_names(clean_data, author_db)
    clean_data = rename_and_select_columns(clean_data)
    clean_data = normalize_numeric_columns(clean_data)
    clean_data = clean_titles(clean_data)
    clean_data = remove_duplicates(clean_data)
    clean_data = remove_rating_outliers(clean_data)
    clean_data = remove_year_outliers(clean_data)
    clean_data = sort_by_rating(clean_data)

    export_as_csv(clean_data, 'data/PROCESSED_DATA.csv')


if __name__ == '__main__':
    main()
