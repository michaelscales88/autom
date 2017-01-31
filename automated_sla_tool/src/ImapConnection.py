from email import message_from_bytes
from tempfile import NamedTemporaryFile
from imaplib import IMAP4_SSL, IMAP4
from pyexcel import get_book
from traceback import format_exc
from datetime import date, datetime


from automated_sla_tool.src.AppSettings import AppSettings


class ImapConnection(IMAP4_SSL):

    def __init__(self, settings, parent):
        conn_info = self._get_conn_settings(settings, parent)
        self._parent = parent
        self._settings = AppSettings(self)
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
        except KeyError:
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

    def __new__(cls, settings, parent):
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

    '''
    Interface
    '''

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

    '''
    Connection Operations
    '''

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
            if hasattr(arg, 'setting'):
                try:
                    conn_info = arg['Connection Info']['Email']
                except KeyError:
                    print('No settings found:\n'
                          '[Connection Info]\n'
                          '[[Email]]\n'
                          'for property: {arg}'.format(arg=arg))
                else:
                    break
        return conn_info

    '''
    Email Operations
    '''

    def _make_data(self, email_info):
        return {
            'from': email_info.get('From', None),
            'dt': email_info.get('Date', None),
            'subject': email_info.get('Subject', None),
            'message': self._get_message(email_info),
            'payload': self._get_payload(email_info)
        }

    def _get_message(self, email_info):
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
                        # wf = wav.open('output.wav', mode='wb')
                        # wf.setparams((wo.getparams()))
                        # for i in range(0, wo.getnframes()):
                        #     wf.writeframes(wo.readframes(i))
                        # wf.close()
                        # print('closed wav file')
                        # (nchannels, sampwidth, framerate, nframes, comptype, compname) = wo.getparams()
                        # wf = wav.open('output.wav', 'wb')

                        # print(type(wf))
                        # wf.close()
                        # print(f.name)
                        # print(file_magic.from_file(f.name))
                        payload[f_name] = f
                    #     stream = PyAudio()
                # if part.get_content_type() == 'audio/wav':
                #     with wav.open(mode='rb') as f:
                #         f.write(part.get_payload(decode=True))
                #         f.seek(0)
                #         payload[f_name] = get_book(
                #             file_type=f_ext,
                #             file_content=f.read()
                #         )
                #     payload[f_name] = part.get_payload(decode=True)
                # file_magic = magic.Magic(magic_file=r"C:\Users\mscales\Desktop\Development\automated_sla_tool\magic.mgc")
                # with NamedTemporaryFile(mode='w+b', suffix=f_ext) as f:
                #     f.write(part.get_payload(decode=True))
                #     f.seek(0)
                #     if f_ext == 'xlsx':
                #         payload[f_name] = get_book(
                #             file_type=f_ext,
                #             file_content=f.read()
                #         )
                #     if f_ext == 'wav':
                        # print('trying to open wav file')
                        # with wav.open(f, mode='rb') as wo:
                        #     wf = wav.open('output.wav', mode='wb')
                        #     wf.setparams((wo.getparams()))
                        #     for i in range(0, wo.getnframes()):
                        #         wf.writeframes(wo.readframes(i))
                        #     wf.close()
                        #     print('closed wav file')
                        #     # (nchannels, sampwidth, framerate, nframes, comptype, compname) = wo.getparams()
                        #     # wf = wav.open('output.wav', 'wb')

                        #     print(type(wf))
                        #     wf.close()
                        # print(f.name)
                        # print(file_magic.from_file(f.name))
                        # payload[f_name] = f
        return payload

    '''
    Iterator
    '''

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
