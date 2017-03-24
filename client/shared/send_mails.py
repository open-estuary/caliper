#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import HTMLParser
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email.Encoders import encode_base64

from caliper.client.shared import utils


class EmailContext(object):
    fro = ''
    to = []
    subject = ''
    plaintext = ''
    htmltext = ''
    attach = ''

    def __init__(self, fro, to, subject, plaintext, htmltext, attach):
        self.fro = fro
        self.to = to
        self.subject = subject
        self.plaintext = plaintext
        self.htmltext = htmltext
        self.attach = attach

    def _construct_attach_(self, msg):
        # create the MIMEBASE instance and make a attach
        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/')

        # read the attach file and format
        data = open(self.attach)
        file_msg = MIMEBase(maintype, subtype)
        file_msg.set_payload(data.read())
        data.close()
        encode_base64(file_msg)

        # set the title of the attach
        basename = os.path.basename(self.attach)
        file_msg.add_header('Content-Disposition', 'attachment',
                filename=basename)
        msg.attach(file_msg)
        return msg

    def getContext(self):
        msg = MIMEMultipart('related')
        msg['Subject'] = self.subject
        msg['From'] = self.fro
        msg['To'] = ','.join(self.to)
        msg['plaintext'] = self.plaintext
        msg.preamble = 'This is a multi-part message in MIME format'
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)
        # set the plain text
        msgText = MIMEText(self.plaintext, 'plain', 'utf-8')
        msgAlternative.attach(msgText)

        msg = self._construct_attach_(msg)
        # set the image in the text
        # fp = open('test.jpg', 'rb')
        # msgImage = MIMEImage(fp.read())
        # fp.close()
        # msgImage.add_header('Content-ID', '<image1>')
        # msg.attach(msgImage)
        return msg.as_string()


class AuthInfo(object):
    server = ''
    user = ''
    password = ''

    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password


class EmailSender(object):
    def send_mail(self, auth, email):
        smtp = smtplib.SMTP()
        # set the debug level
        # smtp.set_debuglevel(1)
        smtp.connect(auth.server)
        smtp.starttls()
        smtp.ehlo()
        smtp.login(auth.user, auth.password)
        smtp.sendmail(email.fro, email.to, email.getContext())
        smtp.quit()
        return


def send_mails(files):
    server = utils.get_config_value('email_config.cfg', 'login_info', 'server')
    user = utils.get_config_value('email_config.cfg', 'login_info', 'user')
    password = utils.get_config_value('email_config.cfg', 'login_info',
                                        'password')
    auth_info = AuthInfo(server, user, password)
    fro = utils.get_config_value('email_config.cfg', 'email_info', 'from')
    to = utils.get_config_value('email_config.cfg', 'email_info', 'to')
    subject = utils.get_config_value('email_config.cfg', 'email_info',
                                    'subject')
    plain = utils.get_config_value('email_config.cfg', 'email_info',
                                    'plaintext')
    html = utils.get_config_value('email_config.cfg', 'email_info', 'htmltext')
    emailTo = [item for item in to.split(",")]
    email = EmailContext(fro, emailTo, subject, plain, html, files)

    emailSender = EmailSender()
    emailSender.send_mail(auth_info, email)
