import email.mime.multipart
from email.MIMEText import MIMEText
import peewee
import smtplib

import db
import secrets

try:
    q = db.User.select(db.User).join(
            db.DatasetAccess
        ).switch(
            db.User
        ).join(
            db.UserLog,
            on=(   (db.UserLog.user    == db.User.user)
                 & (db.UserLog.dataset == db.DatasetAccess.dataset)
            )
        ).where(
            db.DatasetAccess.dataset    == 1,
            db.DatasetAccess.has_access == 0,
            db.UserLog.action           == 'access_requested'
        ).annotate(
            db.UserLog,
            peewee.fn.Max(db.UserLog.ts).alias('apply_date')
        ).get()

    msg             = email.mime.multipart.MIMEMultipart()
    msg['to']       = secrets.admin_address
    msg['from']     = secrets.from_address
    msg['subject']  = 'Pending Swefreq requests'
    msg['reply-to'] = secrets.reply_to_address
    body            = "There are pending requests for swefreq accounts, please visit http://swefreq.nbis.se"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(secrets.mail_server)
    server.sendmail(msg['from'], [msg['to']], msg.as_string())
except peewee.DoesNotExist:
    pass
except Exception as e:
    print "Can't send email"
    print "e"
