import socket
import ssl
import base64
import quopri
import re
import command
counter = 3


def get_user_data(login, password):
    domain = re.match('(.+?)@(.+)', login).group(2)
    return login, password, domain


def get_socket(domain):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
    sock.settimeout(3)
    sock.connect(("imap.{}".format(domain), 993))
    data = (sock.recv(1024)).decode()
    if data.split(' ')[1] != 'OK':
        raise Exception('Can not connect to the server')
    return sock


def log_in(sock, login, password):
    log = command.Login(sock)
    # sock.sendall('a001 LOGIN {0} {1}\r\n'.format(login, password).encode())
    # data = (sock.recv(1024)).decode()
    # if not 'OK LOGIN Completed' in data:
    #     raise Exception('Log in failed')
    log.execute(login, password)


def select(sock):
    # sock.sendall(b'a002 SELECT INBOX\r\n')
    # while True:
    #     try:
    #         data = (sock.recv(1024)).decode()
    #         count = re.match('.+?(\d+) EXISTS.+?', data, re.DOTALL)
    #         if count:
    #             emails_count = int(count.group(1))
    #     except socket.timeout:
    #         break
    # return emails_count
    sel = command.Select(sock)
    count = sel.execute()
    return count


def fetch(sock, id):
    # global counter
    # msg = 'a' + str(counter) + ' ' + 'FETCH {} BODY[TEXT]\r\n'.format(str(id))
    # sock.sendall(msg.encode())
    # data = ''
    # while True:
    #     try:
    #         new_data = (sock.recv(1024)).decode()
    #         #  if new_data.split(' ')[1] == 'OK':
    #         #      break
    #         # else:
    #         data += new_data
    #     except socket.timeout:
    #         break
    # counter += 1
    # text = re.match('.+?charset=\"(.+?)\"(\r\nContent-Transfer-Encoding: (.+?))?\r\n\r\n(.+?)\r\n.+?', data, re.DOTALL)
    # if text.group(3):
    #     text = decode_strings(text.group(4), text.group(3))
    # else:
    #     text = text.group(4)
    # sock.sendall(('a' + str(counter) + ' ' + 'FETCH {} ENVELOPE\r\n'.format(
    #     str(id))).encode())
    # envelope = (sock.recv(1024)).decode()
    # envelope = re.match('.+?FETCH \(ENVELOPE \("(.+?)" "(=\?(.+?)\?(B|Q)\?)?(.+?)".+?NIL "(.+?)" "(.+?)".+?', envelope, re.DOTALL)
    # if envelope.group(2):
    #     theme = decode_strings(envelope.group(5), envelope.group(4))
    # else:
    #     theme = envelope.group(5)
    # date = envelope.group(1)
    # sender = envelope.group(6) + '@' + envelope.group(7)
    # print(sender + ' ' + theme + ' ' + text)
    # return date, theme, sender, text
    fetch = command.Fetch(sock)
    text = fetch.execute(id)
    date, theme, sender = fetch.execute(id, part='ENVELOPE')
    return date, theme, sender, text


def decode_strings(string, encoding):
    if (encoding == 'base64') | (encoding == 'B'):
        return base64.decodebytes(string.encode()).decode()


def main():
    sock = get_socket('yandex.ru')
    # sock.sendall(b'a001 LOGIN test12316@yandex.ru test108!\r\n')
    # data = (sock.recv(1024)).decode()
    # print(data)
    # sock.sendall(b'a002 SELECT INBOX\r\n')
    # while True:
    #     try:
    #         data = (sock.recv(1024)).decode()
    #         print(data)
    #     except socket.timeout: break
    # print(data)
    # sock.sendall(b'a003 FETCH 2 BODY[TEXT]\r\n')
    # data = (sock.recv(1024)).decode()
    # print(data)
    # data = (sock.recv(1024)).decode()
    # print(data)
    log_in(sock, 'test12316@yandex.ru', 'test108!')
    emails_count = select(sock)
    for i in range(1, emails_count+1):
        date, theme, sender, text = fetch(sock, i)
        print(date + sender + ' ' + theme + ' ' + text)


if __name__ == '__main__':
    main()
