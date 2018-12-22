import getpass
from argparse import ArgumentParser
from imap import ImapClient


class ImapClientCLI:
    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument('-ip', '--ip', dest='ip',
                            action='store', required=True,
                            help='Input IMAP server IP',
                            metavar='IP')
        parser.add_argument('-p', '--port', dest='port', action='store',
                            required=True, help='Input IMAP server port',
                            metavar='PORT')
        parser.add_argument('-l', '--login', dest='login', action='store',
                            required=True, help='Input your login',
                            metavar='LOGIN')
        parser.add_argument('-a', '--append',
                            help="Use this flag if you want "
                                      "to append new email",
                            action='store_true', required=False)
        subparsers = parser.add_subparsers(dest='subparser_name')
        append_parser = subparsers.add_parser('append')
        append_parser.add_argument('-f', '--folder', dest='folder',
                                   action='store',
                                   required=True,
                                   help='Input folder to append email')
        append_parser.add_argument('-m', '--message', dest='message',
                                   action='store', required=True,
                                   help='Input message')
        append_parser.add_argument('-s', '--sender', dest='sender',
                                   action='store', required=True,
                                   help='Input sender')
        append_parser.add_argument('-r', '--receiver', dest='receiver',
                                   action='store', required=True,
                                   help='Input receiver')
        append_parser.add_argument('-t', '--theme', dest='theme',
                                   action='store', required=True,
                                   help='Input theme')
        delete_parser = subparsers.add_parser('delete')
        delete_parser.add_argument('-f', '--folder', dest='folder',
                                   action='store', required=True,
                                   help='Input folder where you want '
                                        'to delete email')
        delete_parser.add_argument('-n', '--number', dest='number',
                                   action='store', required=True,
                                   help='Input number of email '
                                        'you want to delete', type=int)
        download_parser = subparsers.add_parser('download')
        download_parser.add_argument('-f', '--folder', dest='folder',
                                     action='store', required=True,
                                     help='Input folder where you want '
                                     'to download applications')
        download_parser.add_argument('-n', '--number', dest='number',
                                     action='store', required=True,
                                     help='Input number of email from which '
                                           'you want to download applications',
                                     type=int)
        password = getpass.getpass('Insert your password: ')
        args = parser.parse_args()
        self.client = ImapClient(args.ip, args.port, args.login, password)
        self.folders_list = self.make_folder_list()
        if args.subparser_name == 'append':
            self.client.select.execute(args.folder)
            self.client.append.execute(self.folders_list[args.folder],
                                       args.message, args.sender,
                                       args.receiver,
                                       args.theme)
        elif args.subparser_name == 'delete':
            self.client.delete_email(self.folders_list[args.folder],
                                     args.number)
        elif args.subparser_name == 'download':
            self.client.get_attachment(self.folders_list[args.folder],
                                       args.number)
        else:
            s = ''
            for folder in self.folders_list:
                self.client.get_emails(self.folders_list[folder])
                s += folder + '\n\n' + \
                    self.make_emails_list(self.folders_list[folder])
                with open('emails.txt', 'w') as f:
                    f.write(s)

    def make_folder_list(self):
        folders_list = {}
        for i in range(0, len(self.client.folders)):
            folders_list[self.client.folders[i][0]] = self.client.folders[i][1]
        return folders_list

    def make_emails_list(self, folder):
        if folder not in self.client.emails:
            self.client.get_emails(folder)
        s = ''
        for email in self.client.emails[folder]:
            s += '{0}. {1}   {2}   {3}\n'.format(email['id'],
                                                 email['sender'],
                                                 email['theme'],
                                                 email['text'])
            for filename in email['filenames']:
                s += filename + '\n'
        return s


def main():
    client = ImapClientCLI()


if __name__ == '__main__':
    main()
