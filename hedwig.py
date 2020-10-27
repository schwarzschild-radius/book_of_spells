# !/usr/bin/python3

import logging
import mimetypes
import os
import smtplib
import sys
import yaml
import pprint

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mischief_managed import decrypt_blob

class PostBox(object):

    def __init__(self, config):
        self.config = config
        self.body = "EOM"
        self.attached_files = []

    def get_connection(self):
        server = smtplib.SMTP(host=self.config['smtp_server'], port=self.config['smtp_port'])
        logging.debug(server.ehlo())
        logging.debug(server.starttls())
        server.login(user=self.config['user'], password=decrypt_blob(self.config['passwd_file'], self.config['private_key']))
        return server

    def addAttachment(self, attach_file, filename):
        with open(attach_file, 'r')  as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            part.add_header("Content-Disposition", "attachment; filename= {}".format(filename))
            self.attached_files.append(part)
            return part

    def addBody(self, body):
        self.body = body

    def sendMail(self, attach_files):
        msg = MIMEMultipart()
        msg['To'] = self.config['to']
        msg['From'] = self.config['from']
        msg['Subject'] = self.config['subject']
        msg.attach(MIMEText(self.body, "plain"))
        for attach_file in attach_files:
            self.addAttachment(attach_file)
        for attached_file in self.attached_files:
            msg.attach(attached_file)

        text = msg.as_string()
        connection = self.get_connection()
        connection.sendmail(self.config['from'], self.config['to'], text)
        connection.quit()
   
