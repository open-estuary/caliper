#!/usr/bin/env python
# -*- coding:utf-8 -*-

from caliper.client.shared import error, settings
from caliper.server import utils
from caliper.server.hosts import ssh_host


DEFAULT_FOLLOW_PATH = '/var/log/kern.log'
DEFAULT_PATTERNS_PATH = 'console_patterns'
SSH_ENGINE = settings.settings.get_value('TestNode', 'ssh_engine')
_started_hostnames = set()


def create_host(hostname, ssh_user, ssh_pass, ssh_port):
    """auto_monitor=True, follow_paths=None, pattern_paths=None,
    netconsole=False,"""
    # here, ssh_user, ssh_pass and ssh_port are injected in he namespace
    # pylint: disable=E0602
    args = {}
    hostname, args['user'], args['password'], args['port'], args['profile'] = (
            utils.parse_machine(hostname, ssh_user, ssh_pass, ssh_port))

    # by fault, assume we use SSH support
    if SSH_ENGINE == "paramiko":
        from caliper.server.hosts import paramiko_host
        classes = [paramiko_host.ParamokoHost]
    if SSH_ENGINE == 'raw_ssh':
        # ssh_host.AsyncSSHMixin
        classes = [ssh_host.SSHHost, ssh_host.AsyncSSHMixin]
    else:
        raise error.AutoError("Unknown SSH engine %s. Please verify the value"
                               " of the configuration key 'ssh_engine' on the"
                               " .ini file " % SSH_ENGINE)
    # create a custom host class for this machine and return an instance of it
    host_class = type("%s_host" % hostname, tuple(classes), {})
    host_instance = host_class(hostname, **args)

    if hostname not in _started_hostnames:
        host_instance.job_start()
        _started_hostnames.add(hostname)

    return host_instance
