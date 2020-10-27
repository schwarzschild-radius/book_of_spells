#! /usr/bin/python3

import hedwig
import subprocess
from enum import Enum
from tempfile import gettempdir
import yaml
import os

class Status(Enum):
    SUCCESS = 0,
    FAIL = 1

def run_process(command):
    out = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    if out.returncode == 0:
        return (Status.SUCCESS, out.stdout, out.stderr)
    return (Status.FAIL, out.stdout, out.stderr)

def send_howler(config, command):
    howler = hedwig.PostBox(config)
    status, stdout, stderr = run_process(command)
    if status == Status.SUCCESS:
        config["subject"] = config["subject"].format(status = "SUCCESS", command = command[0])
    else:
        config["subject"] = config["subject"].format(status = "FAIL", command = command[0])
        fstderr = open(gettempdir() + "/" + str(os.getpid()) + "_stderr.log")
        f = open(fstderr, 'w')
        f.write(stderr.decode())
        f.close()
        howler.addAttachment(fstderr, command[0] + "_stderr.log")
        f.close()
    print(config["subject"])
    if stdout.decode() != '':
        fstdout = gettempdir() + "/" + str(os.getpid()) + "_stdout.log"
        f = open(fstdout, 'w')
        f.write(stdout.decode())
        f.close()
        howler.addAttachment(fstdout, command[0] + "_stdout.log")
        f.close()
    howler.sendMail([])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", help = "yaml file with mail configuration")
    parser.add_argument("command", help = "command to run")
    args = parser.parse_args()
    with open(args.config_file, 'r') as config_file:
        config = yaml.safe_load(config_file)
        send_howler(config, args.command.split(' '))
