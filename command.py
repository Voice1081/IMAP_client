import socket
import re
import quopri
import base64
from abc import ABCMeta, abstractmethod
text_regex = re.compile('.+?charset=\"(.+?)\"(\r\nContent-Transfer-Encoding: (.+?))?\r\n\r\n(.+?)\r\n.+?', re.DOTALL)
envelope_regex = re.compile('.+?FETCH \(ENVELOPE \("(.+?)" "(=\?(.+?)\?(B|Q)\?)?(.+?)".+?NIL "(.+?)" "(.+?)".+?', re.DOTALL)


class Command(metaclass=ABCMeta):
    counter = 0

    def __init__(self, sock):
        self.sock = sock

    def get_data(self, *args):
        command = self.make_command(*args)
        self.sock.sendall(('a' + str(Command.counter) + ' ' + command + '\r\n')
                          .encode())
        data = ''
        while True:
            try:
                new_data = (self.sock.recv(1024)).decode()
                data += new_data
            except socket.timeout:
                break
        Command.counter += 1
        return data

    @abstractmethod
    def execute(self, *args):
        pass

    @abstractmethod
    def make_command(self, *args):
        pass

    @abstractmethod
    def process_data(self, *args):
        pass


class Login(Command):

    def make_command(self, login, password):
        return 'LOGIN {0} {1}'.format(login, password)

    def execute(self, login, password):
        data = super().get_data(login, password)
        return self.process_data(data)

    def process_data(self, data):
        if not 'OK LOGIN Completed' in data:
            raise Exception('Log in failed')


class Select(Command):

    def make_command(self, name):
        return 'SELECT {}'.format(name)

    def execute(self, name='INBOX'):
        data = super().get_data(name)
        return self.process_data(data)

    def process_data(self, data):
        count = int(re.match('.+?(\d+) EXISTS.+?', data, re.DOTALL).group(1))
        return count


class Fetch(Command):

    def make_command(self, number, part):
        return 'FETCH {} '.format(str(number)) + part

    def execute(self, number, part='BODY[TEXT]'):
        data = super().get_data(number, part)
        return self.process_data(data, part)

    def process_data(self, data, part):
        if part == 'BODY[TEXT]':
            return self.parse_text(data)
        if part == 'ENVELOPE':
            date, theme, sender = self.parse_envelope(data)
            return date, theme, sender

    def parse_text(self, data):
        text = text_regex.match(data)
        if text.group(3):
            text = self.decode_strings(text.group(4), text.group(3))
        else:
            text = text.group(4)
        return text

    def parse_envelope(self, data):
        envelope = envelope_regex.match(data)
        if envelope.group(2):
            theme = self.decode_strings(envelope.group(5), envelope.group(4))
        else:
            theme = envelope.group(5)
        date = envelope.group(1)
        sender = envelope.group(6) + '@' + envelope.group(7)
        return date, theme, sender

    @staticmethod
    def decode_strings(string, encoding):
        if encoding == 'base64' or encoding == 'B':
            return base64.decodebytes(string.encode()).decode()
        if encoding == 'Q':
            return quopri.decodestring(string.encode()).decode()
