The file is empty.
# Repository overview

This repository contains small scripts to process, analyse, and extract keywords from a books dataset.

**Files**
- `process_raw_data.py`: Loads a raw CSV of book records and an author SQLite database (`data/authors.db`), cleans and normalises the data (drops nulls, merges author names, converts numeric fields, removes duplicates and outliers), sorts by rating, and writes the cleaned output to `data/PROCESSED_DATA.csv`.
	- Run: install requirements then run:

```bash
python process_raw_data.py data/RAW_DATA_0.csv
```
	- Notes: The script expects an `author` table in `data/authors.db` with columns `(id, name)`. Output overwrites `data/PROCESSED_DATA.csv`.

- `get_keywords.py`: Loads `data/PROCESSED_DATA.csv`, counts words in book titles, filters stop words, takes the top keywords and saves a bar chart image `top_keywords.png`.
	- Run:

```bash
python get_keywords.py
```

- `analyse_processed_data.py`: Analyses `data/PROCESSED_DATA.csv` to produce two charts — a pie chart of books by decade (`decade_releases.png`) and a bar chart of top authors by total ratings (`top_authors.png`).
	- Run:

```bash
python analyse_processed_data.py
```

- Tests: `test_analysis.py`, `test_get_keywords.py`, and `test_transform.py` contain unit tests for the code. Run the test suite with `pytest`.

- `requirements.txt`: Lists Python packages required (e.g., `pandas`, `altair`, `stop-words`, etc.).

**Data folder**
- `data/RAW_DATA_*.csv`: Example raw inputs.
- `data/PROCESSED_DATA.csv`: Output from `process_raw_data.py` (also used as input for the analysis/keyword scripts).
- `data/authors.db`: (expected) SQLite DB containing an `author` table used by `process_raw_data.py`.

**Setup & run**
1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Process raw data, then run analysis/keyword scripts (order matters):

```bash
python process_raw_data.py data/RAW_DATA_0.csv
python get_keywords.py
python analyse_processed_data.py
```

4. Run tests:

```bash
pytest
```

**Notes & troubleshooting**
- The scripts expect Python 3.8+ and the `data/` folder to contain the referenced CSVs and `authors.db` where required.
- If a script fails because `data/PROCESSED_DATA.csv` is missing, run `process_raw_data.py` first to generate it.