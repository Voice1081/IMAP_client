import getpass
from imap import imap_client

login = input('Insert your login: ')
password = getpass.getpass('Insert your password: ')
client = imap_client(login, password)
client.get_emails()
for email in client.emails['INBOX']:
    string = '{0}. {1}   {2}   {3}'.format(email['id'], email['sender'],
                                           email['theme'],
                                           email['text'][0:20])
    print(string)

number = int(input('Insert number of email you want to read: '))
email = client.emails['INBOX'][number-1]
string = '{0} {1}   {2}   {3}'.format(email['date'], email['sender'],
                                      email['theme'],
                                      email['text'])
print(string)

