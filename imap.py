import socket
import ssl
import re
import command


class imap_client:
    def __init__(self, ip, port, login, password):
        self.sock = self.get_socket(ip, port)
        self.login = command.Login(self.sock)
        self.select = command.Select(self.sock)
        self.fetch = command.Fetch(self.sock)
        self.list = command.List(self.sock)
        self.append = command.Append(self.sock)
        self.store = command.Store(self.sock)
        self.expunge = command.Expunge(self.sock)
        self.login.execute(login, password)
        self.folders = self.list.execute()
        self.emails = {}

    @staticmethod
    def get_socket(ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
        sock.settimeout(0.5)
        sock.connect((ip, port))
        data = (sock.recv(1024)).decode()
        if data.split(' ')[1] != 'OK':
            raise Exception('Can not connect to the server')
        return sock

    def get_emails(self, name='INBOX'):
        count = self.select.execute(name)
        self.emails[name] = []
        for i in range(1, count+1):
            self.emails[name].append({})
            text = self.fetch.execute(i, 'BODY[TEXT]')
            date, theme, sender = self.fetch.execute(i, 'ENVELOPE')
            self.emails[name][i-1]['text'] = text
            self.emails[name][i-1]['date'] = date
            self.emails[name][i-1]['theme'] = theme
            self.emails[name][i-1]['sender'] = sender
            self.emails[name][i-1]['id'] = i
            self.emails[name][i - 1]['filenames'] = \
                self.fetch.execute(i, part='BODYSTRUCTURE')

    def get_attachment(self, folder, uid):
        filenames = self.emails[folder][uid-1]['filenames']
        for i in range(0, len(filenames)):
            file = self.fetch.execute(uid, 'BODY[{}]'.format(i + 2))
            with open(filenames[i], 'wb') as f:
                f.write(file)

    def delete_email(self, folder, uid):
        self.store.execute(uid)
        self.expunge.execute()
        self.emails[folder].pop(uid-1)
