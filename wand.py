#! /usr/bin/env python3

import subprocess as sp
import os
from time import time
from datetime import timedelta
import tempfile as tmp

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

def run_process_unified_log(command, env={}):
    my_env = {**os.environ.copy(), **env}
    result = {}
    f = tmp.TemporaryFile()
    start_time = time()
    out = sp.Popen(command, shell=True, stderr=f, stdout=f, text=True,
                   env=my_env)
    end_time = time()
    f.seek(0)
    result = {'status': 'Success' if out.returncode else 'Failed',
              'log': f.read().decode(), 'time_elapsed': timedelta(seconds=(end_time - start_time))}
    f.close()
    return result