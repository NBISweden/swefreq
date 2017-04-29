import torndb as database
import secrets
import smtplib
import email.mime.multipart
from email.MIMEText import MIMEText

db = database.Connection(host = secrets.mysqlHost,
                         database = secrets.mysqlSchema,
                         user = secrets.mysqlUser,
                         password = secrets.mysqlPasswd)

tRes = db.query("""select username, email, affiliation, create_date
                   from swefreq.users where not full_user""")
if len(tRes) > 0:
    msg = email.mime.multipart.MIMEMultipart()
    msg['to'] = secrets.ADMIN_ADDRESS
    msg['from'] = secrets.FROM_ADDRESS
    msg['subject'] = 'Pending Swefreq requests'
    msg.add_header('reply-to', secrets.REPLY_TO_ADDRESS)
    body = "There are pending requests for swefreq accounts, please visit http://swefreq.nbis.se"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(secrets.MAIL_SERVER)
    server.sendmail(msg['from'], [msg['to']], msg.as_string())
