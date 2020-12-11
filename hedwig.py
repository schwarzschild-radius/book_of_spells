#! /usr/bin/env python3

import logging
import mimetypes
import os
import smtplib
import sys
import yaml
import pprint
from dns import resolver
import re
import socket

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mischief_managed import decrypt_blob


def get_connection_from_passwd_file(server, port, user, passwd_file, private_key_file):
    server = smtplib.SMTP(host=server, port=port)
    logging.debug(server.ehlo())
    logging.debug(server.starttls())
    server.login(user=user, password=decrypt_blob(passwd_file, private_key_file))
    return server


def get_connection(smtp_server, dns_server):
    all_smtp_hosts = []
    all_smtp_hosts.append(smtp_server)
    smtp_query_result = resolver.query(dns_server)
    for exdata in smtp_query_result:
        smtp_host = exdata.to_text()
        if re.match(r'[0-9.]*', smtp_host):
            smtp_host = socket.gethostbyaddr(smtp_host)

        all_smtp_hosts.append(smtp_host)

    all_smtp_hosts.append('localhost')

    connection = None
    for host in all_smtp_hosts:
        s = smtplib.SMTP(host)
        result = s.noop()
        if type(result) == type(()) and result[0] == 250:
            connection = s
            break

    if connection is None:
        error = RuntimeError('Unable to connect to smtp server')
        raise error

    return connection


def create_mail():
    return MIMEMultipart()


def add_to(mail_object, to_addr):
    mail_object['To'] = to_addr


def add_from(mail_object, from_addr):
    mail_object['From'] = from_addr


def add_subject(mail_object, subject):
    mail_object['Subject'] = subject


def add_body(mail_object, body):
    mail_object.attach(MIMEText(body, "plain"))


def add_attachment_from_file(mail_object, attachments):
    for (filename, attachment) in attachments:
        with open(attachment, 'r') as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            part.add_header("Content-Disposition",
                            "attachment; filename= {}".format(filename))
            mail_object.attach(part)


def add_attachment_from_string(mail_object, filename, content):
    part = MIMEBase("application", "octet-stream")
    part.set_payload(content)
    part.add_header("Content-Disposition",
                    "attachment; filename= {}".format(filename))
    mail_object.attach(part)


def send_mail(connection, mail_object):
    connection.send_message(mail_object)
    connection.quit()
