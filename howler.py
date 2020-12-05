#! /usr/bin/env python3

import hedwig
import subprocess as sp
from enum import Enum
from tempfile import gettempdir
from time import process_time, time
import logging
import yaml
import os
from datetime import datetime, timedelta
import quill
import sys
from io import StringIO


def run_process(command, env={}):
    my_env = {**os.environ.copy(), **env}
    result = {}
    start_time = time()
    out = sp.Popen(command, shell=True, stderr=sp.PIPE, stdout=sp.PIPE, text=True,
                   env=my_env)
    stdout, stderr = out.stdout.read(), out.stderr.read()
    end_time = time()
    result = {'status': 'Success' if stderr == '' else 'Failed',
              'stdout': stdout, 'stderr': stderr, 'time_elapsed': timedelta(seconds=(end_time - start_time))}
    return result


def get_howler_state():
    howler_state = {
        'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    return howler_state


def send_howler(mail_config, command):
    result = run_process(
        command, mail_config['env'] if 'env' in mail_config else {})
    replacements = {**get_howler_state(), **result}
    replacements['command'] = command
    MailMan = hedwig.get_connection_from_passwd_file(
        mail_config['smtp_server'], mail_config['smtp_port'], mail_config['from'], mail_config['passwd_file'], mail_config['private_key']) if config['with_passwd'] else hedwig.get_connection(
        mail_config['smtp_server'], mail_config['dns_server'])
    mail = hedwig.create_mail()
    hedwig.add_from(mail, mail_config['from'])
    hedwig.add_to(mail, mail_config['to'])
    hedwig.add_subject(
        mail, quill.format_string(mail_config['subject'], replacements))
    hedwig.add_body(mail, quill.format_string(
        mail_config['body'], replacements) if 'body' in mail_config else '')
    if result['status'] != 'Success':
        hedwig.add_attachment_from_string(mail, 'stderr.txt', result['stderr'])
    if result['stdout'] != '':
        hedwig.add_attachment_from_string(mail, 'stdout.txt', result['stdout'])
    hedwig.send_mail(MailMan, mail)
    MailMan.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_file", help="yaml file with mail configuration")
    parser.add_argument('--with-passwd', action='store_true',
                        help="Use a password less service")
    parser.add_argument("command", help="command to run")
    args = parser.parse_args()
    with open(args.config_file, 'r') as config_file:
        config = yaml.safe_load(config_file)
        config['with_passwd'] = True if args.with_passwd else False
        send_howler(config, args.command)
