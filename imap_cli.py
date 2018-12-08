import getpass
from imap import imap_client


class imap_client_cli:
    def __init__(self):
        login = input('Insert your login: ')
        password = getpass.getpass('Insert your password: ')
        self.client = imap_client(login, password)
        self.folders_list = self.make_folder_list()
        self.emails_list = {}
        self.choose_folder()

    def make_folder_list(self):
        s = ''
        for i in range(0, len(self.client.folders)):
            s += '{0}. {1}\n'.format(i+1, self.client.folders[i][0])
        return s

    def make_emails_list(self, folder):
        self.client.get_emails(folder)
        s = ''
        for email in self.client.emails[folder]:
            s += '{0}. {1}   {2}   {3}\n'.format(email['id'],
                                                 email['sender'],
                                                 email['theme'],
                                                 email['text'][0:20])
        self.emails_list[folder] = s

    def make_email_string(self, folder, number):
        email = self.client.emails[folder][number - 1]
        s = '{0} {1}   {2}   {3}'.format(email['date'], email['sender'],
                                         email['theme'], email['text'])
        return s

    def choose_folder(self):
        print(self.folders_list)
        number = int(input('Choose folder you want to enter: '))
        folder = self.client.folders[number-1][1]
        append = input('Do you want to append new email in this folder?[yes/no]')
        if append == 'yes':
            self.append(folder)
        self.choose_email(folder)

    def choose_email(self, folder):
        if folder not in self.emails_list:
            self.make_emails_list(folder)
        print(self.emails_list[folder])
        get_back = input('Would you like to return to folder list?[yes/no]')
        if get_back == 'yes':
            self.choose_folder()
        number = int(input('Choose email you want to read: '))
        print(self.make_email_string(folder, number))
        get_back = input('Would you like to return to emails list?[yes/no]')
        if get_back == 'yes':
            self.choose_email(folder)

    def append(self, folder):
        self.client.select.execute(folder)
        sender = input('Print sender: ')
        receiver = input('Print receiver: ')
        subject = input('Print subject: ')
        message = input('Print your message: ')
        self.client.append.execute(folder, message, sender, receiver, subject)


def main():
    client = imap_client_cli()


if __name__ == '__main__':
    main()
