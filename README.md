# CSVSearch
Reads CSV files into SQLite database and provides a simple interface to access, import, and export queries

# Requirements
- [Python v3](https://www.python.org/)
- [PrettyTable](https://code.google.com/p/prettytable/)

# Usage
Running program

    usage: CSVSearch.py [-h] [--version] sqlite csvfiles [csvfiles ...]
    
    positional arguments:
      sqlite      Sqlite Database
      csvfiles    CSV Files to search
    
    optional arguments:
      -h, --help  show this help message and exit
      --version   show program's version number and exit

While inside program

    Enter a query to execute query
    add a ">> [filename]" to write the result to a file
    [import] to import new file
    [tables] to view all tables
    [help] for help
    [quit] to quit