from datetime import datetime, date, time, timedelta
from dateutil.parser import parse
from automated_sla_tool.src.BucketDict import BucketDict
from automated_sla_tool.src.UtilityObject import UtilityObject
import pyexcel as pe
from automated_sla_tool.src.ReportUtilities import ReportUtilities
from automated_sla_tool.src.TupleKeyDict import TupleKeyDict
import os
import re
from glob import glob as glob
from socket import *
import multiprocessing
from dateutil.parser import parse
import time
import sys
from queue import Queue
import sqlite3
import logging
import logging.config
import iso8601
from os import path
from os.path import basename
from automated_sla_tool.src.AppSettings import AppSettings
from automated_sla_tool.src.InternalDb import InternalDb
from time import sleep
from collections import defaultdict, OrderedDict
from automated_sla_tool.src.utilities import valid_dt
import speech_recognition as sr
from pyexcel import Sheet, get_book
from automated_sla_tool.src.SqlWriter import SqlWriter as ps_write
import pypyodbc as py
import types
from urllib.request import urlopen
import requests
from automated_sla_tool.src.SlaReport import SlaReport
from automated_sla_tool.src.GenericUi import GenericUi as Ui
from automated_sla_tool.src.SqlWriter import SqlWriter as PgConn
from automated_sla_tool.src.timeit import timeit
from dateutil.parser import parse
from re import split
from types import MethodType
from subprocess import Popen
# from automated_sla_tool.src.AudioTranscription import AudioTranscription
from json import dumps
from pyexcel_io import get_data
from pyexcel import Sheet
import platform

# Settings path
_settings = r'C:\Users\mscales\Desktop\Development\automated_sla_tool\automated_sla_tool\settings\SlaReport'
# GOOGLE_CLOUD_SPEECH_CREDENTIALS = r""""installed":{"client_id":"766872889458-u869th48ktiifumrk5ek2a7lp36tb04r.apps.googleusercontent.com","project_id":"encoded-vista-156916","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"bTvPefgEbqvc5k11JcoeAhSJ","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}"""
# GOOGLE_CLOUD_SPEECH_CREDENTIALS = path.join(
#     r'C:\Users\mscales\Desktop\Development\automated_sla_tool\automated_sla_tool\settings',
#     'client_secret_766872889458-u869th48ktiifumrk5ek2a7lp36tb04r.apps.googleusercontent.com.json')
# def get_config(config_path, name):
#     logging.config.dictConfig(config_path)
#     return logging.getLogger(name)
#
#
# class Test:
#     def __init__(self):
#         self._finished = False
#
#     @property
#     def finished(self):
#         return self._finished
#
#     def set_finished(self):
#         self._finished = True
#
#     def run(self):
#         print('running..')
#
#
# def test_fn(stuff):
#     for thing in stuff:
#         print(thing)
#     print('something')
#
# class Point(object):
#     def __init__(self, x, y):
#         self.x, self.y = x, y
#
#     def __conform__(self, protocol):
#         if protocol is sqlite3.PrepareProtocol:
#             return "%f;%f" % (self.x, self.y)
#
#
# def worker():
#     p = multiprocessing.current_process()
#     print('worker {0} {1}'.format(p.name, datetime.now().time()))
#     sys.stdout.flush()
#     time.sleep(2)
#     print('worker {0} {1}'.format(p.name, datetime.now().time()))
#     sys.stdout.flush()
#
#
# class SqlCommand(object):
#     def __init__(self):
#         super().__init__()
#         self._name = None
#         self._cmd = None
#
#     def __repr__(self):
#         return self._cmd
#
#     @property
#     def cmd(self):
#         return self._cmd
#
#     @cmd.setter
#     def cmd(self, cmd):
#         self._cmd = cmd
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, name):
#         self._name = name
# AUDIO_FILE = path.join(r'C:\Users\mscales\Downloads', "man1_nb.wav")
AUDIO_FILE = path.join(r'C:\Users\mscales\Downloads', "MSG00053.wav")
FILEPATH = r'C:\Users\mscales\Desktop\Development\automated_sla_tool\Attachment Archive\2017\0320\Group Abandoned Calls.xlsx'


def filter_row(row_index, row):
    result = [element for element in row if element != '']
    return len(result) == 0


@timeit
def print_stuff(stuff):
    print(stuff)


def common_keys(*dcts):
    for i in set(dcts[0]).intersection(*dcts[1:]):
        yield (i,) + tuple(d[i] for d in dcts)


def test_method(self, something_else):
    print(self, something_else)


def yielder(match_val='something1'):
    test1 = {
        'test1': {
           [
               {
                   'something1': 'value1',
                   'something3': 'value2'
               },
               {
                   'something1': 'value1',
                   'something4': 'value5'
               }
           ]
        },
        'test2': {
            [
                {
                    'something1': 'value1',
                    'something2': 'value2'
                },
                {
                    'something1': 'value1',
                    'something2': 'value2'
                }
            ]
        },
        'test3': {
            [
                {
                    'something1': 'value1',
                    'something2': 'value2'
                },
                {
                    'something1': 'value1',
                    'something2': 'value2'
                }
            ]
        },
        'test6': {
            [
                {
                    'something1': 'value1',
                    'something2': 'value2'
                },
                {
                    'something1': 'value1',
                    'something2': 'value2'
                }
            ]
        }
    }
    test2 = {
        'test1': {
           [
               {
                   'something1': 'value1',
                   'something2': 'value2'
               },
               {
                   'something1': 'value1',
                   'something2': 'value2'
               }
           ]
        },
        'test2': {
           [
               {
                   'something1': 'value1',
                   'something2': 'value2'
               },
               {
                   'something1': 'value1',
                   'something2': 'value2'
               }
           ]
        },
        'test3': {
           [
               {
                   'something1': 'value1',
                   'something2': 'value2'
               },
               {
                   'something1': 'value1',
                   'something2': 'value2'
               }
           ]
        },
        'test4': {
            [
                {
                    'something1': 'value1',
                    'something2': 'value2'
                },
                {
                    'something1': 'value1',
                    'something2': 'value2'
                }
            ]
        }
    }
    for items in common_keys(test1, test2):
        print(items)

    indexed = {}
    for top_key in test1.keys():
        lvl = test2.get(top_key)
        if lvl:
            print(lvl)
            for lvl_item in test1[top_key]:
                print(lvl_item)

    #     indexed[test1[key][match_val]] = item
    # for item in shortest_list:
    #     if item[match_val] in indexed:
    #         yield item, indexed[item[match_val]]


class Test(object):

    bound_settings = []

    @staticmethod
    def curr_keyword():
        return Test.bound_settings

    @staticmethod
    def bind_settings(settings):
        Test.bound_settings = settings

    @staticmethod
    def header_filter(row_index, row):
        keyword = Test.curr_keyword()
        print(keyword)
        corner_case = split('\(| - ', row[0])
        bad_word = corner_case[0].split(' ')[0] not in keyword
        return True if len(corner_case) > 1 else bad_word


def test():
    print(platform.system() == 'Windows')
    # test = ReportUtilities()
    # test.open_focus('excel', FILEPATH)
    # test.open_directory(FILEPATH)
    # test.open_directory(r"C:\Users\mscales\Desktop\Development\automated_sla_tool\Attachment Archive\2017\0320")
    # test.open_directory(r"C:\Users\mscales\Desktop\Development\automated_sla_tool\Attachment Archive\2017\0320")
    # test.open_directory(r"M:\Help Desk\Daily SLA Report")
    # test.open_directory(FILEPATH)
    # return
    # now = datetime.now().time()
    # later = (datetime.now() + timedelta(minutes=30)).time()
    # both = now + later
    # print(
    #     'Now', now
    # )
    # print(
    #     'Later', later
    # )
    # print(
    #     'Now + later {}'.format()
    # )
    # sheet = pe.Sheet(
    #     [
    #         ['A', 'B', 'C'],
    #         ['B', 'B', 'C'],
    #         ['C', 'B', 'C'],
    #     ]
    # )
    # print(sheet)
    # sheet[1, 1] = [
    #         2, 5
    #     ]
    # sheet[1, 1] = sum(value for value in sheet[1, 1])
    # print(sheet)
    # print(sheet)
    # settings = AppSettings(file_name=_settings)
    # print(dumps(settings, indent=4))
    # for items in settings.at_lvl('Clients'):
    #     print(items)
    # print(settings['Clients'])
    # for items in settings.setting('Clients'):
    #     print(items)
    #     print(type(items))
    #     print(hasattr(items, 'items'))

    # Active Testing

    # test = {
    #     x: fn_test() for x in range(5)
    # }
    #
    # print(dumps(test, indent=4))
    # return
    # my_ui = Ui()
    # my_ui.object = SlaReport(test_mode=True)
    # my_ui.object = ps_write()
    # my_ui.run()

    # x = AudioTranscription()
    #
    # for text in x.transcribe([AUDIO_FILE]):
    #     print(text)
    # with get_book(file_name=FILEPATH) as book:
    #     print(book)

    # with open(FILEPATH, mode='rb') as book2:
    #     book = get_book(file_content=book2, file_type='xlsx')
    #     for sheet in book:
    #         print(sheet)
    #     # print(book)
    # Popen('explorer "{0}"'.format(r'C:\Users\mscales\Desktop\Development\automated_sla_tool\Attachment Archive\2017\0320'))
    # input('Any key to continue.')
    # Other Testing
    # FILEPATH2 = r'C:\Users\mscales\Desktop\Development\automated_sla_tool\Attachment Archive\2017\0310\Cradle to Grave.xlsx'
    # file = pe.get_book(file_name=FILEPATH2)
    # try:
    #     file.remove_sheet('blarnsballs')
    # except KeyError:
    #     print('I realized it wasnt in there')
    # test1 = Test()
    # test1.bind_settings(['Feature', 'Call', 'Event'])
    # # test1.bound_settings.append(['Feature', 'Call', 'Event'])
    # print(test1.bound_settings)
    # # bound_header_filter = MethodType(header_filter, stuff)
    # workbook = pe.get_book(file_name=FILEPATH2)
    # workbook.remove_sheet('Summary')
    # for sheet_name in reversed(workbook.sheet_names()):
    #     sheet = workbook.sheet_by_name(sheet_name)
    #     # del sheet.row[bound_header_filter]
    #     del sheet.row[test1.header_filter]
    #     sheet.name_rows_by_column(0)
    #     sheet.name_columns_by_row(0)
    # print(workbook)
    # print(test1.bound_settings)
        # try:
        #     self.chck_rpt_dates(sheet)
        # except ValueError:
        #     workbook.remove_sheet(sheet_name)
    # FILEPATH1 = r'C:\Users\mscales\Desktop\Development\automated_sla_tool\Attachment Archive\2017\0310\Group Abandoned Calls.xlsx'
    # test = pe.get_sheet(file_name=FILEPATH1)
    # print(test)
    # FILEPATH2 = r'C:\Users\mscales\Desktop\Development\automated_sla_tool\Attachment Archive\2017\0310\Cradle to Grave.xlsx'
    # test2 = pe.get_sheet(file_name=FILEPATH2)
    # print(test2)
    # yielder()
    # for item1, item2 in yielder():
    #     print(item1)
    #     print(item2)
    # test1 = AppSettings(file_name='SlaReport')
    # print(test1)
    # test1.test()
    # print('completed format')
    # print(test1)
    # sheet = get_book(file_name=FILEPATH)
    # print(sheet.__class__.__name__ == 'Book')
    # jar = requests.RequestsCookieJar()
    # login_info = {'user': 'ops_mscales', 'pw': 'wireless!'}
    # with requests.Session() as s:
    #     s.post('http://insidemw.com:21120/default.aspx', data=login_info)
    #     html = s.get(r'http://insidemw.com:21120/edit_bug.aspx?id=5855316')
    #     print(html.text)
    # r = requests.get('http://insidemw.com:21120/', params=login_info)
    # r = requests.post('http://insidemw.com:21120/', data=login_info)
    # print(r.headers['content-type'])
    # print(r.encoding)
    # print(r.text)
    # print(r.json())
    # html = urlopen(r'http://insidemw.com:21120/edit_bug.aspx?id=5855316')
    # print(html.read().decode('utf-8'))
    # testfile = request.URLopener()
    # testfile.retrieve("http://randomsite.com/file.gz", "file.gz")
    # conn_string = {
    #     'DRIVER': '{SQL Server}',
    #     'DATABASE': 'IssueTracker',
    #     'UID': 'IssueTrackerWeblogin',
    #     'PWD': 'mw!2006',
    #     'SERVER': '10.1.3.43'
    # }
    # creating connection Object which will contain SQL Server Connection
    # connection = py.connect('Driver={SQL Server};Server=10.1.3.43;Database=IssueTracker;uid=IssueTrackerWeblogin;pwd=mw!2006')
    # print(connection)
    # conn_string = {
    #     'DATABASE': 'chronicall',
    #     'UID': 'Chronicall',
    #     'PWD': 'ChR0n1c@ll1337',
    #     'SERVER': '10.1.3.17',
    #     'PORT': '9086'
    # }
    # query = '''
    # select bp_file, isnull(bp_content_type,'') [bp_content_type]
    # from bug_posts
    # where bp_id = 24115415
    # and bp_bug = 5855316;
    # '''
    # conn = ps_write(**conn_string)
    # wav_file = conn.exc_cmd(query)
    # f_path = r'C:/Users/Mscales/Desktop/test.wav'
    # with open(f_path, mode='w+b') as f:
    #     f.write(wav_file.fetchone()[0])
    #     f.seek(0)
    # thing = 'string1'
    # meth = types.MethodType(test_method, thing)
    # meth('other thing')
    # bound_handler = test_method.__get__(self, thing)
    # book = pe.get_book(file_name=FILEPATH)
    # for sheet in book:
    #     print(sheet)
    # for sheet_name in book.sheet_names():
    #     sheet = book.sheet_by_name(sheet_name)
    #     print(sheet)
    # from os import getcwd
    # wav_f = path.join(getcwd(), 'MSG00053.wav')
    # with open(wav_f) as f:
    #     print(type(f))
    # email = get_email_data(settings=AppSettings(settings_file=_settings))
    # print(email)
    # for k, v in email.items():
    #     print(k)
    #     print(v)
    # conn = InternalDb()
    # print(conn.get_tables())
    # r = sr.Recognizer()
    # with sr.AudioFile(AUDIO_FILE) as source:
    #     audio = r.record(source)  # read the entire audio file
    #
    # # recognize speech using Google Cloud Speech
    #     try:
    #         print("Google Cloud Speech thinks you said {speech}".format(speech=r.recognize_google_cloud(audio)))
    #     except sr.UnknownValueError:
    #         print("Google Cloud Speech could not understand audio")
    #     except sr.RequestError as e:
    #         print("Could not request results from Google Cloud Speech service; {0}".format(e))

    # string_test = 'Voicemail Message (8472243850 > Danaher) From:8472243850Fri, 13 Jan 2017 07:08:43 -0600'
    # # print(iso8601.parse_date(string_test))
    # dt = valid_dt(string_test.split(',')[1])
    # print(dt)
    # print(type(dt))
    # str1 = ''
    # str2 = 'stuff'
    # print(str1.isalpha())
    # print(str2.isalpha())
    # from os import makedirs
    # from os.path import isfile
    # f_path1 = 'C:/Users/Mscales/Desktop/test_file'
    # f_path = 'C:/Users/Mscales/Desktop/test_file.txt'
    # print(isfile(f_path))
    # makedirs(f_path1, exist_ok=True)
    # print(isfile(f_path))
    # print(not True)
    # print(not False)
    # test_list= []
    # print(test_list.__sizeof__())
    # test_list.append(0)
    # test_list.append(0)
    # test_list.append(0)
    # print(test_list.__sizeof__())
    # import re
    # s = "alpha.Customer[cus_Y4o9qMEZAugtnW] ..."
    # m = re.search(r"\[([A-Za-z0-9_]+)\]", s)
    # print(m.group(1))
    # s = 'stuff stuff (1235) stuff'
    # matches = re.search(r"([0-9]+)", s)
    # print(matches.group(0))
    # sheet = pe.Sheet(colnames=['', 'stuff'])
    # rows = [
    #     ['row_name1', 'stuff_value3'],
    #     ['', ''],
    #     ['row_name2', 'stuff_value1'],
    #     ['row_name3', 'stuff_value3'],
    #     ['', ''],
    #     ['row_name4', 'stuff_value'],
    #     ['row_name5', 'stuff_value2'],
    #     ['row_name6', 'stuff_value'],
    #     ['row_name7', 'stuff_value2'],
    #     ['', ''],
    #     ['row_name8', 'stuff_value']
    # ]
    # for row in rows:
    #     sheet.row += row
    # sheet.name_rows_by_column(0)
    # print(sheet)
    # del sheet.row[filter_row]
    # print(sheet)
    # # for row_name in sheet.rownames:
    # #     if sheet[row_name, 'stuff'] == 'stuff_value1':
    # #         sheet.delete_named_row_at(row_name)
    # # print(sheet)
    # i_count = {}
    # for row_name in reversed(sheet.rownames):
    #     caller = sheet[row_name, 'stuff']
    #     # i_count[caller] = {
    #     #     'count': i_count.get(caller, 0).get('count', 0) + 1,
    #     #     ''
    #     # }
    #     dup_info = i_count.get(caller, {'count': 0,
    #                                     'call_ids': []})
    #     dup_info['count'] += 1
    #     dup_info['call_ids'].append(caller)
    #     i_count[caller] = dup_info
    # print(i_count)
    # string1 = 'string'
    # string2 = '123'
    # print(string1.isdigit())
    # print(string2.isdigit())
    # _log_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), r'settings\logging2.conf')
    # print(_log_path)
    # log = SysLog(__file__, file_path=_log_path)
    # print(log)
    # test_sheet = pe.Sheet()
    # test_sheet.row += [['', 'A', 'B', 'C', 'D'],
    #                    [1, 2, 3, 4, 5],
    #                    [6, 7, 8, 9, 10]]
    # test_sheet.name_columns_by_row(0)
    # test_sheet.name_rows_by_column(0)
    # print(test_sheet)
    # for i, column in enumerate(test_sheet.columns()):
    #     print(test_sheet.colnames[i])
    #     print(column)
    # im_a_dict = {
    #     'value': 0
    # }
    # if im_a_dict['value']:
    #     print('i evaluated to true')
    # print(im_a_dict['value'] is False)
    # sheet = pe.Sheet(colnames=['', 'a', 'b', 'c', 'd'])
    # tuple_ex = (test_fn, 'stuff', 'stuff2')
    # fn = tuple_ex[:1]
    # other_stuff = tuple_ex[1:]
    # print(fn)
    # print(other_stuff)
    # tuple_ex[:1](other_stuff)
    # key = 'stuff'
    # thing1 = key[0]
    # thing2 = key[2]
    # print(thing1)
    # print(thing2)
    # sheet = pe.Sheet(colnames=['', 'a', 'b', 'c', 'd'])
    # rownames = ['a', 'b', 'c', 'd']
    # print(['row'] + [0 for x in range(len(sheet.colnames)-1)])
    # for row in rownames:
    #     sheet.row += [row] + [0 for x in range(len(sheet.colnames)-1)]
    # sheet.name_rows_by_column(0)
    # print(sheet)
    # rows = [
    #     ['{i}'.format(i=chr(i * (x+1) + 97)) for x in reversed(range(5))] for i in range(5)
    # ]
    # for row in rows:
    #     sheet.row += row
    # for x in range(3):
    #     sheet.row += [x, '0', '0', '0', '0']
    # sheet.name_rows_by_column(0)
    # print(sheet)
    # for i, row in enumerate(sheet.rownames):
    #     sheet.set_row_at(i, ['a', 'b', 'c', 'd'])
    # print(sheet)
    # print(sheet.rownames)
    # print(sheet.colnames)
    # print(sheet)
    # sheet.colnames += ['e', 'f']
    # print(sheet.colnames)
    # new_rows = [
    #     ['e', 'f'],
    #     ['1', '2'],
    #     ['2', '2'],
    #     ['3', '3'],
    #     ['4', '4'],
    #     ['5', '5']
    #     # ['', 'e', 'f'],
    #     # ['a', '1', '2'],
    #     # ['f', '2', '2'],
    #     # ['k', '3', '3'],
    #     # ['p', '4', '4'],
    #     # ['u', '5', '5']
    # ]
    # new_sheet = pe.Sheet(new_rows)
    # new_sheet.name_rows_by_column(0)
    # new_rows = OrderedDict(
    #     [
    #         ('e', ['1', '2', '3', '4', '5']),
    #         ('f', ['1', '2', '3', '4', '5'])
    #     ]
    # )
    # print(new_rows)
    # new_sheet.name_rows_by_column(0)
    # sheet.column['e'] += new_sheet.column['e']
    # sheet.column['f'] += new_sheet.column['f']
    # sheet.extend_columns(new_rows)
    # print(sheet)
    # print(sheet.column['e'])
    # sheet.column += new_sheet
    # print(sheet)
    # conn_string = {
    #     'DATABASE': 'chronicall',
    #     'UID': 'Chronicall',
    #     'PWD': 'ChR0n1c@ll1337',
    #     'SERVER': '10.1.3.17',
    #     'PORT': '9086'
    # }
    # tables = ['c_call', 'c_event', 'c_feature']
    # commands = []
    # raw_commands = {
    #     k: datetime.today().date() for k in tables
    # }
    # for k, v in raw_commands.items():
    #     cmd = SqlCommand()
    #     cmd.name = k
    #     cmd.cmd = (
    #         '''
    #         SELECT *
    #         FROM {t}
    #         WHERE to_char({t}.start_time, 'YYYY-MM-DD') = '{v}'
    #         '''.format(t=cmd.name, v=v.strftime('%Y-%m-%d'))
    #     )
    #     commands.append(cmd)
    # from automated_sla_tool.src.SqliteWriter import SqliteWriter as sq_lite
    # conn = ps_write(**conn_string)
    # conn.replicate_to(dest_conn=sq_lite(), sql_commands=commands)
    # new_conn = sq_lite()
    # print(new_conn.query('c_call'))
    # print(new_conn.query('c_event'))
    # print(new_conn.query('c_feature'))
    # string = 'Call ID - 12312412'
    # import re
    # string = 'Cradle to, Grave - stuff'
    # corner_case = re.split(', | - ', string)
    # print(corner_case)
    # first_split = string.split(' - ')
    # second_split = first_split[0].split(' ')
    # print(second_split)
    # check_one = second_split[0] not in ('Feature', 'Call', 'Event')  # False
    # print(len(first_split))
    # print(True if len(first_split) > 1 else check_one)
    # input_opt = OrderedDict(
    #     [('Today', 0),
    #      ('Tomorrow', 1),
    #      ('Yesterday', -1)]
    # )
    # input_opt2 = ['Today', ]
    # selection = list(input_opt.values())
    # chc = selection[
    #         int(
    #             input(
    #                 ''.join(['{k}: {i}\n'.format(k=k, i=i) for i, k in enumerate(input_opt)])
    #             )
    #         )
    #     ]
    # print(
    #     date.today() + timedelta(days=chc)
    # )
    # from automated_sla_tool.src.FinalReport import FinalReport
    # rpt = FinalReport(report_date=date.today(), report_type='sla_report')
    # print(rpt.name)
    # rpt.name = 'something else'
    # print(rpt.name)
    # rpt.save_as('C:/Users/mscales/desktop/test.xlsx')
    # print(
    #     [0 for x in range(10)]
    # )


    print('Complete')


if __name__ == "__main__":
    test()
