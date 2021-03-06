#!/usr/bin/python
from prettytable import from_db_cursor
from io import BytesIO
from time import sleep
import argparse
import sqlite3
import csv
import sys
import os

__author__ = 'Kyle Bloom'
__version__ = '1.0'

USAGE = '''
Enter a query to execute query
['query' >> 'file']  write the query result file
['query' >> !]       suppresses output
[import 'file']      import new file
[columns 'table']    view columns in table
[tables]             view all tables
[help]               display help
[quit]               quit
String Commands together with the ';'
'''


def cls():
    """Clears Screen based on system type"""
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def sqlsafenames(string, replacements=None):
    """Removes replacements from string
    or if no replacements are passed it replaces
    ' ', '-', '#', and '%' with
    '_', '_', 'NUM', and 'PERCENT' respectively

    Parameters
    ----------
    string : str
        String to replace with replacements
    replacements : dict of str's
        Dictionary with the substring to extract as key and substring to replace as value

    Return
    ------
    str
        string with every part in replacements replaced
    """
    if not replacements:
        replacements = {
            ' ': '_',
            '-': '_',
            '#': 'NUM',
            '%': 'PERCENT'
        }
    for item in replacements:
        string = string.replace(item, replacements[item])
    return string


def dict_factory(cursor, row):
    """Creates a dictionary from a row and cursor

    Parameters
    ----------
    cursor : python db cursor
    row : python db row

    Return
    ------
    dict
        Dictionary with a string key and db object value
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def addtable(csvfile, database, name=None, pattern=None):
    """Adds table based on CSV file information

    Parameters
    ----------
    csvfile : str file path
        Path to CSV File
    database : python database object
    name : str
        Name for new table
    pattern : str
        Comma seperated list of column names
    """
    cursor = database.cursor()
    if not name:
        name = sqlsafenames(os.path.basename(csvfile.name).split('.')[0])
    csvdict = csv.DictReader(csvfile)
    if not pattern:
        field = []
        for item in csvdict.fieldnames:
            field.append(sqlsafenames(item))
        pattern = ', '.join(field)
    sqldelete = 'DROP TABLE IF EXISTS {name};'.format(name=name)
    sqlcreate = 'CREATE TABLE {name} ({pattern});'.format(name=name, pattern=pattern)
    cursor.execute(sqldelete)
    cursor.execute(sqlcreate)
    for row in csvdict:
        field = []
        items = []
        for item in row:
            field.append(sqlsafenames(item))
            items.append(row[item])
        sqlinsert = 'INSERT INTO {name} ({fields}) VALUES ({data})'.format(
            name=name,
            fields=', '.join(field),
            data=','.join('?' * len(items)))
        cursor.execute(sqlinsert, items)


def writeresults(cursor, fn):
    """Writes Sql Results[cursor] to CSV File[fn]

    Parameters
    ----------
    cursor : python db cursor
    fn : file ojbect
    """
    table = cursor.fetchall()
    fn.write('{0}\n'.format(','.join([item[0] for item in cursor.description])))
    for row in table:
        fn.write('{0}\n'.format(','.join([item for item in row])))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sqlite',
                        type=str,
                        nargs='?',
                        default=':memory:',
                        help='SQLite Database (:memory: or - to run in memory only)')
    parser.add_argument('files',
                        metavar='csvfiles',
                        type=argparse.FileType('r'),
                        nargs='*',
                        default=[],
                        help='CSV Files to search')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-c', '--command',
                        type=str,
                        help='run\'s commands and quits',
                        default=None)
    args = parser.parse_args()
    if args.sqlite == '-':  # Replace with in memory SQLite flag
        args.sqlite = ':memory:'
    database = sqlite3.connect(args.sqlite)
    for fn in args.files:
        addtable(fn, database)
        fn.close()
    database.commit()
    cursor = database.cursor()
    if not sys.stdin.isatty():  # Check if pipe stdin is connected to a terminal or if it is piped data
        tty = BytesIO()
        tty.write(sys.stdin.read())
        tty.seek(0)
        addtable(tty, database, name='input')
        if not args.command:  # If data was piped in but there was no sql statement was supplied return table
            args.command = 'SELECT * FROM input >>'
    if args.command:
        try:
            with open(args.command, 'r') as datalist:
                data = datalist.read()
                data += ';quit'
        except IOError:
            data = args.command + ';quit'
    else:
        data = 'help'
    while True:
        data = data.split(';')
        for query in data:
            query = query.strip()
            if query.lower() in ('quit', 'exit'):
                sys.exit(0)
            # region Basic Funcitons
            if query.lower() in ('h', 'help'):
                sys.stdout.write(USAGE)
            elif query.lower() == 'clear':
                cls()
            elif query.lower() == 'version':
                sys.stdout.write(' '.join([os.path.basename(sys.argv[0]), __version__]) + os.linesep)
            # endregion

            # region Table Information
            elif query.lower() == 'tables':
                cursor.execute('SELECT name FROM sqlite_master WHERE type = \'table\'')
                sys.stdout.write(str(from_db_cursor(cursor)) + os.linesep)
            elif query.lower()[:7] == 'columns':
                try:
                    table = query.split(' ', 1)
                except IndexError:
                    sys.stderr.write('No table name provided [columns \'table\']' + os.linesep)
                    table = None
                except Exception as e:
                    sys.stderr.write('Unknown Error: {0}'.format(str(e)))
                    table = None
                if type(data) is list:
                    cursor.execute('PRAGMA table_info({0})'.format(table[1]))
                    sys.stdout.write(str(from_db_cursor(cursor)) + os.linesep)
            # endregion

            # region Import new file
            elif query.lower()[:6] == 'import':
                try:
                    filename = query.split(' ', 1)[1]
                except IndexError:
                    sys.stderr.write('No file name provided [import \'filename\']' + os.linesep)
                    filename = None
                except Exception as e:
                    sys.stderr.write('Unknown Error: {0}'.format(str(e)))
                    filename = None
                if os.access(filename, os.R_OK):
                    addtable(open(filename, 'r'), database)
                elif filename is not None:
                    sys.stderr.write('"{0}" is not a valid file{1}'.format(filename, os.linesep))
            # endregion

            # region Run Query
            else:
                try:
                    todo = query.split('>>')
                    cursor.execute(todo[0])
                    if len(todo) == 1:
                        if todo[0].strip()[:6].lower() == 'select' and todo[0].strip()[-1:] != '!':
                            sys.stdout.write(str(from_db_cursor(cursor)) + os.linesep)
                        else:
                            sys.stdout.write('Command Successful' + os.linesep)
                    else:
                        if not todo[1]:
                            writeresults(cursor, sys.stdout)
                        else:
                            filename = open(todo[1].strip(), 'w+')
                            writeresults(cursor, filename)
                            filename.close()
                except Exception as e:
                    sys.stderr.write('Unknown Error: {0}{1}'.format(str(e), os.linesep))
            # endregion
            sleep(.01)
        sys.stdout.write(os.linesep + '>>> ')
        sys.stdout.flush()
        data = sys.stdin.readline()
        data = data.strip()
    database.commit()
    database.close()
