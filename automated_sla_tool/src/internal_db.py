import sqlite3 as lite
from datetime import time, datetime
from automated_sla_tool.src.query_writer import QueryWriter


class InternalDb(QueryWriter):

    def __init__(self, **parameters):
        super().__init__()
        self.path = self.fnd_dir()
        self.init_params(**parameters)
        self.ci = {
            None: 'NULL',
            int: 'INTEGER',
            float: 'REAL',
            str: 'TEXT',
            time: 'TEXT',
            datetime: 'DATETIME'
        }  # Command Interpreter Python/SQLite
        self.connect()

    def init_params(self, **kwargs):
        conn_string = '{path}\{db}.db'.format(path=self.path,
                                              db=kwargs.get('local_db', 'test'))
        self._params['local_db'] = conn_string

    def copy_tables(self, columns, data):
        try:
            self.create_table(data.name, columns)
        except lite.OperationalError:
            pass
        self.insert_data(data)

    def create_table(self, table_name, columns_w_meta):
        val_type = ', '.join(['{value} {type}'.format(value=k, type=self.ci[v]) for k, v in columns_w_meta.items()])
        cmd = ('CREATE table {t} '
               '({c})'.format(t=table_name, c=val_type))
        self._conn.execute(cmd)
        self.commit_changes()

    def insert_data(self, data):
        print('Starting insert {name} {time}'.format(name=data.name, time=datetime.now().time()), flush=True)
        ph = ', '.join([':{0}'.format(k) for k in data.colnames])
        cmd = ('INSERT INTO {t} VALUES ({values});'.format(t=data.name,
                                                           values=ph))
        self._conn.executemany(cmd, data.rows())
        self.commit_changes()
        print('Finished insert {name} {time} # rows: {num_rows}'.format(name=data.name,
                                                                        time=datetime.now().time(),
                                                                        num_rows=data.number_of_rows()), flush=True)

    def query(self, table_name):
        cmd = '''
        SELECT count(ROWID)
        FROM {t}
        '''.format(t=table_name)
        columns, data = self.get_data(cmd)
        data.name = table_name
        return data

    def query2(self, table_name):
        cmd = '''
        SELECT *
        FROM {t}
        '''.format(t=table_name)
        columns, data = self.get_data(cmd)
        data.name = table_name
        return data

    def query_col_names(self):
        cmd = "pragma table_info('{}')".format(input('table?'))
        for row in self._conn.execute(cmd).fetchall():
            print(row)

    def drop_table(self, table_name):
        if self.check_exists(table_name):
            cur = self._conn.cursor()
            cmd = "DROP table '{0}'".format(table_name)
            cur.execute(cmd)
            self._conn.commit()
            self.refresh_connection()

    def check_exists(self, table_name):
        cmd = "SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(table_name)
        return len(self.exc_cmd(cmd).fetchall()) > 0

    def get_tables(self):
        cur = self._conn.cursor()
        cur.row_factory = lambda cursor, row: row[0]
        cmd = "SELECT name FROM sqlite_master WHERE type='table'"
        cur.execute(cmd)
        return cur.fetchall()

    def get_conn(self):
        return lite.connect(self._params['local_db'])

    def commit_changes(self):
        self._conn.commit()
        self.refresh_connection()

    def fnd_dir(self):
        import os
        path = os.path.normpath(os.getcwd())
        tgt_dir = path.split(os.sep)
        db_dir = None
        while len(tgt_dir) > 1:
            if tgt_dir[-1] == tgt_dir[-2]:
                db_dir = '{dir}\db'.format(dir='\\'.join(tgt_dir))
                if os.path.isdir(db_dir):
                    break
            else:
                tgt_dir.pop(-1)
        return 'No dB directory' if db_dir is None else db_dir