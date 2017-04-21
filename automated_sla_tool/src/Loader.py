from glob import glob
from os.path import join, splitext
from datetime import timedelta


from .Downloader import Downloader


class Loader:
    def __init__(self):
        self._conn = None
        self._cwd = None

    @property
    def cwd(self):
        return self._cwd

    @cwd.setter
    def cwd(self, new_wd):
        self._cwd = new_wd

    @property
    def connection(self):
        return self._conn

    @connection.setter
    def connection(self, new_conn):
        self._conn = new_conn

    def load(self, unloaded_files):
        loaded_files = {}
        for f_name in reversed(unloaded_files):
            src_f = glob(r'{f_path}*.*'.format(f_path=join(self.cwd, f_name)))
            if len(src_f) is 1:
                unloaded_files.remove(f_name)
                loaded_files[f_name] = {
                    'path': src_f[0],
                    'ext': splitext(src_f[0])[1][1:]
                }
        return loaded_files

    def load_or_dl(self, unloaded_files):
        print('entering load or dl')
        loaded_files = self.load(unloaded_files)
        print(loaded_files)
        if len(unloaded_files) > 0:
            print('about to download')
            Downloader(parent=self.connection).get_f_list(self.connection.interval + timedelta(days=1),
                                                          unloaded_files)
        for key, values in {**loaded_files, **self.load(unloaded_files)}.items():
            yield key, values['path'], values['ext']