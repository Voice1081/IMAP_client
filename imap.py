import socket
import ssl
import re
import command


class imap_client:
    def __init__(self, login, password):
        domain = self.get_domain(login)
        self.sock = self.get_socket(domain)
        self.login = command.Login(self.sock)
        self.select = command.Select(self.sock)
        self.fetch = command.Fetch(self.sock)
        self.list = command.List(self.sock)
        self.login.execute(login, password)
        self.folders = self.list.execute()
        self.emails = {}

    @staticmethod
    def get_domain(login):
        domain = re.match('(.+?)@(.+)', login).group(2)
        return domain

    @staticmethod
    def get_socket(domain):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
        sock.settimeout(3)
        sock.connect(("imap.{}".format(domain), 993))
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


def main():
    a = imap_client('test12316@yandex.ru', 'test108!')
    a.get_emails()


if __name__ == '__main__':
    main()
