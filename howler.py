#! /usr/bin/env python3

import hedwig
import subprocess as sp
from enum import Enum
from tempfile import gettempdir
from time import process_time, time
import logging
import yaml
import os
from datetime import datetime
import quill
import json
import wand


def get_howler_state():
    howler_state = {
        'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
    return howler_state


def send_regular_message(config, command, just_status=True):
    result = wand.run_process_without_log(
        command, config['env'] if 'env' in config else {})
    status = result['status']
    data = ''
    if not just_status:
        data = result['log']
    else:
        data = command
    message = {
        "text":
        "status: {}\ndata: {}\ntime_elapsed: {}".format(
            status, data, result['time_elapsed'])
    }
    if hedwig.slack_through_webhook(config['slack_webhook_url'],
                                    json.dumps(message)):
        print("slack message sent failed")


def send_howler(config, command):
    result = wand.run_process_with_unified_log(
        command, config['env'] if 'env' in config else {})
    replacements = {**get_howler_state(), **result}
    replacements['command'] = command
    MailMan = hedwig.get_connection_from_passwd_file(
        config['smtp_server'], config['smtp_port'], config['from'],
        config['passwd_file'], config['private_key']
    ) if config['with_passwd'] else hedwig.get_connection(
        config['smtp_server'], config['dns_server'])
    mail = hedwig.create_mail()
    hedwig.add_from(mail, config['from'])
    hedwig.add_to(mail, config['to'])
    hedwig.add_subject(mail,
                       quill.format_string(config['subject'], replacements))
    hedwig.add_body(
        mail,
        quill.format_string(config['body'], replacements)
        if 'body' in config else '')
    hedwig.add_attachment_from_string(mail, 'log.txt', result['log'])
    hedwig.send_mail(MailMan, mail)
    MailMan.close()


def dispatch_work(config, command):
    payload_types = config['hedwig_payload_type']
    for payload_type in payload_types:
        if payload_type == 'mail':
            send_howler(config, command)
        elif payload_type == 'slack_status':
            send_regular_message(config, command)
        elif payload_type == 'slack':
            send_regular_message(config, command, False)
        else:
            print("Invalid payload type {}".format(payload_type))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file",
                        help="yaml file with mail configuration")
    parser.add_argument('--with-passwd',
                        action='store_true',
                        help="Use a password less service")
    parser.add_argument("command", help="command to run")
    args = parser.parse_args()
    with open(args.config_file, 'r') as config_file:
        config = yaml.safe_load(config_file)
        config['with_passwd'] = True if args.with_passwd else False
        dispatch_work(config, args.command)
