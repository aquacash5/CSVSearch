# CSVSearch
Reads CSV files into SQLite database and provides a simple interface to access, import, and export queries

[![Code Issues](https://www.quantifiedcode.com/api/v1/project/551645450e054369a835933708532c44/badge.svg)]
(https://www.quantifiedcode.com/app/project/551645450e054369a835933708532c44)

# Requirements
- [Python](https://www.python.org/) v2.6 or greater
- [PrettyTable](https://code.google.com/p/prettytable/)

# Usage
Running program

    usage: CSVSearch.py [-h] [--version] [-c COMMAND]
                    [sqlite] [csvfiles [csvfiles ...]]

    positional arguments:
      sqlite                SQLite Database (:memory: or - to run in memory only)
      csvfiles              CSV Files to search

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -c COMMAND, --command COMMAND
                            run's commands and quits

     alternatively you can pipe a csv file into this and output a query to a pipe

While inside program

    Enter a query to execute query
    ['query' >> 'file']  write the query result file
    ['query' >> !]       suppresses output
    [import 'file']      import new file
    [columns 'table']    view columns in table
    [tables]             view all tables
    [help]               display help
    [quit]               quit
    String Commands together with the ';'
