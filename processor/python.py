#!/usr/bin/env python

import yaml
import sys
from string import Template
import os
from os.path import isfile, join, splitext
import copy
import re
import chkcrontab_lib as check
import subprocess
import tempfile



def load(yaml_file):
    f = open(yaml_file)
    data = yaml.safe_load(f)
    f.close()
    return data


def validate_cron(file_path):
    whitelisted_users = None
    log = check.LogCounter()
    return check.check_crontab(file_path, log, whitelisted_users)


def convert_memlimit(value):
    if not isinstance(value, str):
        return value
    match = re.match(r"(\d+)[Mm][Bb]", value)
    if match:
        return int(match.group(1)) * pow(10, 6)

    return value


def convert_cpushares(value):
    return value


def substitute_all(values, string):
    if isinstance(string, str):
        template = Template(string)
        return template.safe_substitute(values)
    else:
        return string


def merge(source, destination):
    """
    Recursive map merge
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination


def convert(file):
    command = ['kompose', '--suppress-warnings',
               '-f', file, 'convert', '--rc', '--stdout', '--yaml']
    try:
        res = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return yaml.safe_load(res)
    except subprocess.CalledProcessError as err:
        print(file)
        with open(file, 'r') as fin:
            print(fin.read())
    except yaml.scanner.ScannerError as err:
        print(' '.join(command))
        print(res)
        raise err


def compose(file_name, yaml_doc):
    user = 'root'

    if not os.path.exists('.jobs'):
        os.makedirs('.jobs')

    if not os.path.exists('.jobs/cron'):
        os.makedirs('.jobs/cron')

    if not os.path.exists('.jobs/job'):
        os.makedirs('.jobs/job')

    config = copy.deepcopy(global_config)
    merge(yaml_doc.pop("Configuration", {}), config)

    cron_file = ".jobs/cron/" + file_name.lower()
    cron = file(cron_file, 'w')
    cron.write('SHELL=/bin/sh\n')
    cron.write('PATH=/usr/local/sbin:/usr/local/bin'
               ':/sbin:/bin:/usr/sbin:/usr/bin\n')

    for grouping, data in yaml_doc.iteritems():  # use safe_load instead load
        defaults = copy.copy(global_defaults)
        jobs = data.pop('Jobs')
        defaults.update(data)

        for job in jobs:
            jobName, jobData = job.popitem()
            jobName = jobName.lower()
            if os.path.exists('./jobs/job/' + jobName):
                print('A job of this name already exists {0}'.format(jobName))
                exit(2)

            dump = {'environment': {'job': jobName}}

            merge(defaults, dump)
            time = dump.pop('time', None)
            if isinstance(jobData, str):
                time = jobData
            else:
                merge(jobData, dump)
                time = dump.pop('time', time)

            for key, value in dump.iteritems():
                dump[key] = substitute_all(dump['environment'], value)

            if "mem_limit" in dump:
                dump["mem_limit"] = convert_memlimit(dump["mem_limit"])
                dump['environment']['mem_limit'] = str(dump['mem_limit'])

            stream = tempfile.NamedTemporaryFile()
            # Write a YAML representation of data to 'document.yaml'.
            yaml.dump({jobName: dump}, stream, default_flow_style=False)
            pods = convert(stream.name)
            stream.close()

            # Set image pull policy to always if image is latest
            for pod in pods['items']:
                pod['kind'] = 'Job'
                pod['apiVersion'] = 'extensions/v1beta1'
                pod.pop('status')
                pod['spec'].pop('replicas')
                if 'spec' in config:
                    merge(config['spec'], pod['spec']['template']['spec'])
                if 'annotations' in config:
                    pod['metadata']['annotations'] = {}
                    merge(config['annotations'],
                          pod['metadata']['annotations'])

                for container in pod['spec']['template']['spec']['containers']:
                    if container['image'].endswith(":latest"):
                        container['imagePullPolicy'] = 'Always'

            stream = file(".jobs/job/" + jobName + ".yaml", 'w')
            yaml.dump(pod, stream, default_flow_style=False)
            stream.close()

            if time:
                text = "{0} {1} /app/runner {2}" \
                       " >> /var/log/cron.log 2>&1\n"
                cron.write(text.format(time, user, jobName))
    cron.write('#Cron needs a newline at the end')
    cron.close()

    validation_log = validate_cron(cron_file)
    if validation_log:
        print(validation_log)
        exit(9)


global global_defaults
global global_config

global_defaults = {}
global_config = {}

cmdargs = sys.argv[1]

default_file = "{0}/DEFAULTS.yaml".format(cmdargs)


if isfile(default_file):
    loaded_defaults = load(default_file)
    global_config = loaded_defaults.pop("Configuration", {})
    global_defaults = loaded_defaults

for f in os.listdir(cmdargs):
    path = join(cmdargs, f)
    if isfile(path) and (path.endswith(".yaml") or path.endswith(".yml")):
        yaml_doc = load(path)
        filename, file_extension = splitext(f)
        if filename != 'DEFAULTS':
            compose(filename, yaml_doc)
