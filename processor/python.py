#!/usr/bin/env python

import yaml
import sys
from string import Template
import os
from os.path import isfile, join, splitext
import copy
import re
import chkcrontab_lib as check

def load(yaml_file):
    f = open(yaml_file)
    data = yaml.safe_load(f)
    f.close()
    return data

def validate_cron(file_path):
    whitelisted_users = None
    log = check.LogCounter()
    return check.check_crontab(file_path, log, whitelisted_users)


def validate(yaml_doc):
    return
    #TODO validate all the things
    #TODO consider using pykwalify
    #TODO validate cron time format
    #TODO validate job name works for K8S aka no _
    #sys.exit(1)

def convert_memlimit(value):
    if not isinstance(value, str):
        return value
    match = re.match(r"(\d+)[Mm][Bb]",value)
    if match:
        return int(match.group(1)) * pow(10,6)

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

def compose(file_name, yaml_doc):
    user='root'

    if not os.path.exists('default'):
        os.makedirs('default')

    if not os.path.exists('compose'):
        os.makedirs('compose')

    config = copy.copy(global_config)
    merge(yaml_doc.pop("Configuration", {}), config)

    if not os.path.exists('cron'):
        os.makedirs('cron')
    cron_file = "cron/"+file_name.lower()
    cron = file(cron_file, 'w')
    cron.write('SHELL=/bin/sh\n')
    cron.write('PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n')

    for grouping, data in yaml_doc.iteritems(): # use safe_load instead load
        defaults = copy.copy(global_defaults)
        jobs = data.pop('Jobs')
        defaults.update(data)

        for job in jobs:
            jobName, jobData = job.popitem()
            dump = {'environment': {'job': jobName}}

            merge(defaults, dump)
            time = None
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

            if "cpu_shares" in dump:
                dump["cpu_shares"] = convert_cpushares(dump["cpu_shares"])
                dump['environment']['cpu_shares'] = str(dump['cpu_shares'])

            if os.path.exists('default/'+jobName):
                print('A job of this name already exists {0}'.format(jobName))
                exit(2)


            job_env = file('default/'+jobName, 'w')
            for key, value in config.iteritems():
                job_env.write('{0}="{1}"\n'.format(key,value))
            job_env.close


            stream = file("compose/"+jobName+".yaml", 'w')
            yaml.dump({jobName: dump}, stream, default_flow_style=False)    # Write a YAML representation of data to 'document.yaml'.
            stream.close()

            if time:
                cron.write("{0} {1} /app/processor/runner {2} >> /var/log/cron.log 2>&1\n".format(time,user, jobName))
    cron.write('#Cron needs a newline at the end')
    cron.close()

    validation_log = validate_cron(cron_file)
    if validation_log:
        print(validation_log)
        exit(9)

    if 'SCHEDULED' in config: #If the scheduled key exists skip the cron file
        os.remove("cron/"+file_name.lower())



global global_defaults
global global_config

global_defaults = {}
global_config = {}

cmdargs = sys.argv[1]

default_file="{0}/DEFAULTS.yaml".format(cmdargs)
if isfile(default_file):
    loaded_defaults = load(default_file)
    global_config = loaded_defaults.pop("Configuration", {})
    global_defaults = loaded_defaults

for f in os.listdir(cmdargs):
    path = join(cmdargs,f)
    if isfile(path) and (path.endswith(".yaml") or path.endswith(".yml")):
        yaml_doc=load(path)
        validate(yaml_doc)
        filename, file_extension = splitext(f)
        if filename != 'DEFAULTS':
            compose(filename, yaml_doc)
