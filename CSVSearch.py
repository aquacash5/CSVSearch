#!/usr/bin/python
"""
CSV SQLite Search
Copyright (C) 2015 Kyle Bloom

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

__author__ = 'Kyle Bloom'
__version__ = '0.5'

from prettytable import PrettyTable
from io import StringIO
import argparse
import sqlite3
import csv
import sys
import os


usage = \
    '''
Enter a query to execute query
['query' >> 'file']  write the query result file
[import 'file']      import new file
[columns 'table']    view columns in table
[tables]             view all tables
[help]               display help
[quit]               quit

'''


def cls():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def sqlsafenames(string, replacements=None):
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
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def addtable(csvfile, database,name=None, pattern=None):
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
        sqlinsert = '''
            INSERT INTO {name}
            ({fields}) VALUES ({data})
        '''.format(name=name, fields=', '.join(field), data=','.join('?' * len(items)))
        cursor.execute(sqlinsert, items)


def displaytable(cursor, table):
    headers = []
    for item in cursor.description:
        headers.append(item[0])
    t = PrettyTable(headers)
    for row in table:
        items = []
        for col in range(0, len(row.keys())):
            items.append(row[headers[col]])
        t.add_row(items)
    sys.stdout.write(str(t) + '\n')


def writeresults(cursor, table, file):
    headers = []
    for item in cursor.description:
        headers.append(item[0])
    file.write('{0}\n'.format(','.join(headers)))
    for row in table:
        items = []
        for col in range(0, len(row.keys())):
            items.append(row[headers[col]])
        file.write('{0}\n'.format(','.join(items)))

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
    parser.add_argument('-s', '--sql',
                        type=str,
                        help='run\'s SQL command, outputs csv, and quits',
                        default=None)
    args = parser.parse_args()
    if args.sqlite == '-':
        args.sqlite = ':memory:'
    data = 'help'
    database = sqlite3.connect(args.sqlite)
    database.row_factory = dict_factory
    for file in args.files:
        addtable(file, database)
        file.close()
    database.commit()
    cursor = database.cursor()
    if not sys.stdin.isatty():
        tty = StringIO()
        tty.write(sys.stdin.read())
        tty.seek(0)
        addtable(tty, database, name='input')
        if not args.sql:
            args.sql = 'SELECT * FROM input'
    if args.sql:
        cursor.execute(args.sql)
        writeresults(cursor, cursor.fetchall(), sys.stdout)
        data = 'quit'
    while not data.lower() in ('quit', 'exit', 'q'):
        if data.lower() in ('h', 'help'):
            sys.stdout.write(usage)
        elif data.lower() == 'clear':
            cls()
        elif data.lower() == 'tables':
            cursor.execute('select name from sqlite_master where type = \'table\'')
            displaytable(cursor, cursor.fetchall())
        elif data.lower()[:7] == 'columns':
            try:
                data = data.split(' ', 1)
            except Exception as e:
                sys.stdout.write(e.message + '\n')
                data = None
            if type(data) is list:
                cursor.execute('PRAGMA table_info({0})'.format(data[1]))
                displaytable(cursor, cursor.fetchall())
        elif data.lower()[:6] == 'import':
            try:
                filename = data.split(' ', 1)[1]
            except:
                filename = None
            if not filename:
                sys.stderr.write('Enter a file name after import to import a file\n')
            elif os.access(filename, os.R_OK):
                addtable(open(filename, 'r'), database)
            else:
                sys.stderr.write('"{0}" is not a valid file\n'.format(filename))
        elif data.lower() == 'version':
            sys.stdout.write(' '.join([os.path.basename(sys.argv[0]), __version__]) + '\n')
        else:
            try:
                todo = data.split('>>')
                cursor.execute(todo[0])
                if len(todo) == 1:
                    displaytable(cursor, cursor.fetchall())
                else:
                    filename = open(todo[1].strip(), 'w+')
                    writeresults(cursor, cursor.fetchall(), filename)
                    filename.close()
            except Exception as exp:
                sys.stderr.write(str(exp) + '\n')
        sys.stdout.write('>>> ')
        sys.stdout.flush()
        data = sys.stdin.readline()
        data = data.strip()
    database.commit()
    database.close()
