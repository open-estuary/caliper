#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Date    :   14/12/26 17:14:04
#   Desc    :
#

import utils
import os
import re
import logging

from caliper.client.shared import error

TEE_TO_LOGS = object()


class Host(object):
    job = None

    def __init__(self, *args, **dargs):
        self._initialize(*args, **dargs)

    def _initialize(self, *args, **dargs):
        self._already_repaired = []
        self._removed_files = False

    def setup(self):
        pass

    def close(self):
        pass

    def send_file(self, source, dest, delete_dest=False):
        raise NotImplementedError("Get file not implemented!")

    def get_file(self, source, dest, delete_dest=False):
        raise NotImplementedError("Send File not implemented!")

    def get_tmp_dir(self):
        raise NotImplementedError("Get tmp dir not implemented!")

    def check_diskspace(self, path, gb):
        """Raised an error if path does not have at least gb GB free"""
        one_mb = 10**6
        mb_per_gb = 1000.0
        logging.info('Checking for >= %s GB od space under %s on machine %s',
                    gb, path, self.hostname)
        df = self.run('df -PB %d %s | tail -l' % (one_mb, path)).stdout.split()
        free_space_gb = int(df[3]) / mb_per_gb
        if free_space_gb < gb:
            raise error.ServDiskFullHostError(path, gb, free_space_gb)
        else:
            logging.info('Found %s GB >= %s GB of space under %s on "\
                            "machine %s' % (free_space_gb, gb, path,
                            self.hostname))

    def run(self, command, timeout=7200, ignore_status=False,
            stdout_tee=TEE_TO_LOGS, stderr_tee=TEE_TO_LOGS,
            stdin=None, args=()):
        """
        :param ignore_status: do not raise an exception, no matter
            what the exit code of the command is.
        :param stdout_tee/stderr_tee: where to tee the stdout/stderr
        :param args: sequence of strings to pass as arguments to command by
                        quoting them in '' and escaping their contents if
                        necessary
        :return: CmdResult object
        """
        raise NotImplementedError('Run not implemented!')

    def run_output(self, command, *args, **dargs):
        return self.run(command, *args, **dargs).stdout.rstrip()

    def disable_ipfilters(self):
        self.run('iptables-save >/ tmp/iptable-rules')
        self.run('iptables -P INPUT ACCEPT')
        self.run('iptables -P FORWARD ACCEPT')
        self.run('iptables -P OUTPUT ACCEPT')

    def enable_ipfilters(self):
        if self.path_exists('/tmp/iptables-runles'):
            self.run('iptables-restore < /tmp/iptable-runles')

    def install(self, installableObject):
        installableObject.install(self)

    def get_autodir(self):
        raise NotImplementedError('Got autodir not implemented!')

    def set_autodir(self):
        raise NotImplementedError('Set autodir not implemented!')

    def start_loggers(self):
        """Called to start continuous host logging"""
        pass

    def stop_loggers(self):
        """Called to stop continuous host logging"""
        pass

    # some extra methods simplify the retrieval of information about the
    # Host machine, with generic implementations based on run(). subclasses
    # should feel free to override these if they can provide better
    # implementations for their specific Host types
    def get_num_cpu(self):
        """ Get the number of CPUs in the host according to /proc/cpuinfo. """
        proc_cpuinfo = self.run('cat /proc/cpuinfo',
                                    stdout_tee=open(os.devnull, 'w')).stdout
        cpus = 0
        for line in proc_cpuinfo.splitlines():
            if line.startswith('processor'):
                cpus += 1
        return cpus

    def get_arch(self):
        """ Get the hardware architecture of the remote machine. """
        arch = self.run('/bin/uname -m').stdout.rstrip()
        if re.match(r'i\d86$', arch):
            arch = 'i386'
        return arch

    def get_kernel_ver(self):
        """ Get the kernel version of the remote machine. """
        return self.run('/bin/uname -r').stdout.rstrip()

    def get_cmdline(self):
        """ Get the kernel command line of the remote machine. """
        return self.run('cat /proc/cmdline').stdout.rstrip()

    def get_meminfo(self):
        """ Get the kernel memory info (/proc/meminfo) of the remote machine
            and return a dictionary mapping the various statistics. """
        meminfo_dict = {}
        meminfo = self.run('cat /proc/meminfo').stdout.splitlines()
        for key, val in (line.split(':', 1) for line in meminfo):
            meminfo_dict[key.strip()] = val.strip()
        return meminfo_dict

    def path_exists(self, path):
        """Determine if path existes on the remote machien"""
        result = self.run('ls %s > /dev/null' % utils.sh_escape(path),
                            ignore_status=True)
        return result.exit_status == 0
