import smtplib
from smtplib import SMTP_SSL as SMTP
import mimetypes
import os
import datetime
import email
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import encoders

import conf
counter = 0


def send_email(conf, m):
    try:
        if conf.email_port == 25:
            s = smtplib.SMTP(conf.email_server, conf.email_port)
        elif conf.email_port == 587:
            s = smtplib.SMTP(conf.email_server, conf.email_port)
            s.ehlo()
            s.starttls()
            s.ehlo()
        elif conf.email_port == 465:
            s = smtplib.SMTP_SSL(conf.email_server, conf.email_port)
        else:
            return False
        s.set_debuglevel(conf.debuglevel)
        s.login(conf.from_addr, conf.passwd)
        s.sendmail(conf.from_addr, conf.alert, m.as_string())
        s.quit()
        print ('successfully sent the email')
        return True
    except:
        return False

# main program
for dirname, dirnames, filenames in os.walk(conf.path):
    for filename0 in filenames:
        if conf.pattern in filename0:
            counter = 1
            # email header
            m = MIMEMultipart()
            m['To'] = conf.to_addr
            m['From'] = conf.from_addr
            m['Subject'] = conf.subject_header
            date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            body = 'This is the email body. Sent on %s.' % (date)
            m.attach(MIMEText(body))
            # attaching text file to email body
            fp = open(conf.path+'/'+filename0, 'rb')
            msg = MIMEBase('multipart', 'plain')
            msg.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(msg)
            msg.add_header('Content-Disposition',
                           'attachment', filename=filename0)
            m.attach(msg)
            # send email
            if not send_email(conf, m):
                print ("failed to send email")
            # delete file ?
            if conf.delete_files:
                os.remove(conf.path+'/'+filename0)

    # better alert than do nothing ;)
    if counter == 0:
        # email header
        m = MIMEMultipart()
        m['To'] = conf.alert
        m['From'] = conf.from_addr
        m['Subject'] = conf.subject_alert
        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        body = 'Error sending email attachment. Sent on %s.' % (date)
        m.attach(MIMEText(body))
        # send email
        if not send_email(conf, m):
            print ("failed to send mail")
