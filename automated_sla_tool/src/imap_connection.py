from email import message_from_bytes
from tempfile import NamedTemporaryFile
from imaplib import IMAP4_SSL, IMAP4
from pyexcel import get_book
from traceback import format_exc
from datetime import date, datetime
from os.path import join, isfile


from automated_sla_tool.src.app_settings import AppSettings


class ImapConnection(IMAP4_SSL):

    def __init__(self, settings=None, parent=None):
        conn_info = self._get_conn_settings(settings, parent)
        self._parent = parent
        self._settings = AppSettings(app=self)
        try:
            print(
                'Attempting to connect to {conn_type} : {connection}'.format(
                    conn_type=conn_info['login_type'],
                    connection=conn_info['user_name']
                )
            )
            super().__init__(conn_info['login_type'])
            self._attempt_login(conn_info['user_name'], conn_info['pw'])
        except AttributeError:
            print(
                'No settings found for EmailGetter.'
            )
        except (KeyError, TypeError):
            print(
                'No connection information provided for EmailGetter.'
            )
        except IMAP4.error as e:
            print(
                'Encountered {e} during connection to:\n'
                '{conn_type} : {connection}\n'
                '{error_log}'.format(
                    e=e,
                    conn_type=conn_info('login_type', 'No connection type provided.'),
                    connection=conn_info('user_name', 'No email to connect to.'),
                    error_log=format_exc()
                )
            )
        else:
            self.go_to_box('Inbox')

    def __new__(cls, settings=None, parent=None):
        try:
            return parent.instances[cls] if cls in parent.instances else super().__new__(cls)
        except AttributeError:
            return super().__new__(cls)

    def __del__(self):
        try:
            print('Trying to close connection: {conn}'.format(conn=self))
            self.close()
            self.logout()
            print('Closed connection: {conn}'.format(conn=self))
        except (AttributeError, IMAP4.error):
            print('No connection to close.')
        finally:
            ImapConnection._conn_set = False

    @property
    def parent(self):
        return self._parent

    # Interface
    def go_to_box(self, tgt_box):
        return self.select(tgt_box)

    def all_ids(self, on):
        all_ids = {}
        passes = 0
        for email_info in self._search(on, 'ALL'):
            an_id = self._make_data(email_info)
            all_ids[an_id['subject']] = an_id
            if passes > 4:
                break
            passes += 1
        return all_ids

    def read_ids(self, on):
        read_ids = {}
        for email_info in self._search(on, 'SEEN'):
            read_id = self._make_data(email_info)
            read_ids[read_id['subject']] = read_id
        return read_ids

    def unread_ids(self, on):
        unread_ids = {}
        for email_info in self._search(on, 'UNSEEN'):
            unread_id = self._make_data(email_info)
            unread_ids[unread_id['subject']] = unread_id
        return unread_ids

    def get_ids(self, on, get):
        rtn_ids = {}
        for email_info in self._search(on, get):
            rtn_id = self._make_data(email_info)
            rtn_ids[rtn_id['subject']] = rtn_id
        return rtn_ids

    # Connection Operations
    def _attempt_login(self, username, password):
        attempts = 3
        while attempts:
            try:
                r, d = self.login(username, password)
            except IMAP4.error:
                attempts -= 1
                print('There was an issue logging into: {cnx}'
                      '\n{tries} attempts remaining.'.format(cnx=username,
                                                             tries=attempts))
            else:
                conn_info = '\n'.join(
                    [
                        '{id}: {cnx}'.format(id=num, cnx=str(i, encoding='utf-8')) for num, i in enumerate(d, start=1)
                        ]
                )
                print(
                    'Connection Status: {status}'
                    '\n{conns}'.format(
                        status=r,
                        conns=conn_info
                    )
                )
                break

    @staticmethod
    def _get_conn_settings(*args):
        conn_info = None
        for arg in args:
            try:
                if hasattr(arg, 'setting'):
                    conn_info = arg['Connection Info']['Email']
                    break
                if hasattr(arg, 'settings'):
                    conn_info = arg.settings['Connection Info']['Email']
                    break
            except (AttributeError, KeyError):
                print('No settings found:\n'
                      '[Connection Info]\n'
                      '[[Email]]\n'
                      'for property: {arg}'.format(arg=arg))
        return conn_info

    # Email Operations
    def _make_data(self, email_info):
        return {
            'from': email_info.get('From', None),
            'dt': email_info.get('Date', None),
            'subject': email_info.get('Subject', None),
            'message': self._get_message(email_info),
            'payload': self._get_payload(email_info)
        }

    @staticmethod
    # TODO combine this into _get_payload
    def _get_message(email_info):
        message = ''
        for part in email_info.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_type() == 'text/plain':
                message += str(part.get_payload(decode=True),
                               encoding=str(part.get_content_charset())).replace('<br/>', '\n')
        return message

    def _get_payload(self, email_info):
        payload = {}
        for part in email_info.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            f_name = part.get_filename()
            f_ext = self._settings['Content Type'].get(part.get_content_type(), None)
            # See if its possible to get f_ext from .get_content_charset()
            if f_name and f_ext:
                if f_ext == 'xlsx':
                    try:
                        f_path = join(self.parent.src_doc_path, f_name)
                        if not isfile(f_path):
                            with open(f_path, mode='wb') as f:
                                f.write(part.get_payload(decode=True))
                                f.close()
                        payload[f_name] = get_book(
                            file_name=f_path
                        )
                    except AttributeError:
                        with NamedTemporaryFile(mode='w+b', suffix=f_ext) as f:
                            f.write(part.get_payload(decode=True))
                            f.seek(0)
                            payload[f_name] = get_book(
                                file_type=f_ext,
                                file_content=f.read()
                            )
                if f_ext == 'wav':
                    with NamedTemporaryFile(mode='w+b', suffix=f_ext) as f:  # change this back to delete=False for scribing
                        f.write(part.get_payload(decode=True))
                        f.seek(0)
                        payload[f_name] = f
        return payload

    # Iterator
    def _search(self, look_for, status):
        if isinstance(look_for, (date, datetime)):
            on = 'ON {date}'.format(date=look_for.strftime("%d-%b-%Y"))
            result, data = self.uid('search', on, status)
            if result == 'OK':
                for uid in data[0].split():
                    result, data = self.uid('fetch', uid, '(RFC822)')
                    if result == 'OK':
                        yield (message_from_bytes(data[0][1]))
        else:
            print('No datetime or date provided for EmailGetter._search')
