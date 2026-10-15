# CSV Cleaner (Python)

[![Tests](https://github.com/biltekinhamza/csv-cleaner/actions/workflows/tests.yml/badge.svg)](https://github.com/biltekinhamza/csv-cleaner/actions/workflows/tests.yml)

A small command-line tool that cleans messy CSV files. Pure Python standard library, no
dependencies, covered by unit tests.

## What it does
- Normalizes header names (`" First  Name "` -> `first_name`)
- Trims cells and collapses repeated spaces inside them
- Removes completely empty rows
- Removes exact duplicate rows (compared after cleaning)
- Pads short rows; stops with a clear error if a row has more columns than the header
- Handles the invisible BOM character that Excel adds to CSV files
- Prints a short summary of what was changed

## Usage
```
python csv_cleaner.py sample/messy.csv
python csv_cleaner.py sample/messy.csv -o result.csv
python csv_cleaner.py data.csv --delimiter ";"
```

## Example
Input `sample/messy.csv`:
```
  First Name , LAST   NAME,Email ,City
  Ann ,Miller, ann@example.com ,Berlin
Bob,  Stone,bob@example.com,  Paris
,,,
Ann,Miller,ann@example.com,Berlin
Carla,   Diaz,carla@example.com,Madrid
   ,   ,   ,
bob,Stone,bob@example.com,Paris
```
Output `sample/messy_clean.csv`:
```
first_name,last_name,email,city
Ann,Miller,ann@example.com,Berlin
Bob,Stone,bob@example.com,Paris
Carla,Diaz,carla@example.com,Madrid
bob,Stone,bob@example.com,Paris
```
Console summary:
```
Rows read:          7
Empty rows removed: 2
Duplicates removed: 1
Rows written:       4
```

## Limitations
- Duplicates are matched exactly, so `Bob` and `bob` count as different rows.
- Cell values are kept as text; no type conversion or date parsing.

## Tests
```
pip install -r requirements.txt
pytest
```
