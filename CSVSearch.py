#/bin/python
__author__ = 'Kyle Bloom'
__version__ = '0.3'

from prettytable import PrettyTable
import argparse
import sqlite3
import csv
import sys
import os


usage = 'Enter a query to execute query\n' \
        'add a ">> [filename]" to write the result to a file\n' \
        '[import] to import new file\n' \
        '[tables] to view all tables\n' \
        '[help] for help\n' \
        '[quit] to quit\n'


def cls():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def addtable(csvfile, database, pattern=None):
    cursor = database.cursor()
    name = os.path.basename(csvfile.name).split('.')[0].replace(' ', '_')
    csvdict = csv.DictReader(csvfile)
    if not pattern:
        fields = []
        for item in csvdict.fieldnames:
            fields.append(item.replace(' ', '_').replace('#', 'NUM'))
        pattern = ', '.join(fields)
    sqldelete = 'DROP TABLE IF EXISTS {name};'.format(name=name)
    sqlcreate = 'CREATE TABLE {name} ({pattern});'.format(name=name, pattern=pattern)
    cursor.execute(sqldelete)
    cursor.execute(sqlcreate)
    for row in csvdict:
        field = []
        items = []
        for item in row:
            field.append(item.replace(' ', '_').replace('#', 'NUM'))
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
                        help='SQLite Database (:memory: to run in memory only)')
    parser.add_argument('files',
                        metavar='csvfiles',
                        type=argparse.FileType('r'),
                        nargs='*',
                        help='CSV Files to search',
                        default=[])
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-s', '--sql',
                        type=str,
                        help='Run\'s SQL command, outputs csv, and quits')
    args = parser.parse_args()
    database = sqlite3.connect(args.sqlite)
    database.row_factory = dict_factory
    for file in args.files:
        addtable(file, database)
        file.close()
    database.commit()
    cursor = database.cursor()
    data = 'help'
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
        sys.stdout.write('>>> \r')
        data = sys.stdin.readline()
        data = data.strip()
