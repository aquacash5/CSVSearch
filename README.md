# CSVSearch
Reads CSV files into SQLite database and provides a simple interface to access, import, and export queries

# Requirements
- [Python](https://www.python.org/) v2.6 or greater
- [PrettyTable](https://code.google.com/p/prettytable/)

# Usage
Running program

    usage: CSVSearch.py [-h] [--version] [-s SQL] sqlite [csvfiles [csvfiles ...]]

    positional arguments:
      sqlite             SQLite Database (:memory: or - to run in memory only)
      csvfiles           CSV Files to search

    optional arguments:
      -h, --help         show this help message and exit
      --version          show program's version number and exit
      -s SQL, --sql SQL  run's SQL command, outputs csv, and quits

While inside program

    Enter a query to execute query
    add a ">> [filename]" to write the result to a file
    [import] to import new file
    [tables] to view all tables
    [help] for help
    [quit] to quit
