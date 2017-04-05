#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import urllib

from caliper.client.shared import error
from caliper.server.hosts import basic_host
from caliper.server import utils

DEFAULT_HALT_TIMEOUT = 50
DEFAULT_REBOOT_TIMEOUT = 120
LAST_BOOT_TAG = None


class RemoteHost(basic_host.Host):
    """
    this class means a remote machine on which you can run programs
    it may be accessed through a network, a serial line, ...
    """
    VAR_LOG_MESSAGES_COPY_PATH = "/var/tmp/messages.caliper_start"
    VAR_LOG_MESSAGES_PATHS = ["/var/log/messages"]

    def _initialize(self, hostname, autodir=None, profile='', *args, **dargs):
        super(RemoteHost, self)._initialize(*args, **dargs)
        self.hostname = hostname
        self.autodir = autodir
        self.profile = profile
        self.tmp_dirs = []

    def __repr__(self):
        return "<remote host: %s, profile: %s>" % (self.hostname, self.profile)

    def close():
        super(RemoteHost, self).close()
        self.stop_loggers()

        if hasattr(self, 'tmp_dirs'):
            for dir in self.tmp_dirs:
                try:
                    self.run('rm -fr "%s"' % utils.sh_escape(dir))
                except error.AutoError:
                    pass

    def _var_log_messages_path(self):
        """
        Find possible paths for a message file
        """
        for path in self.VAR_LOG_MESSAGES_PATHS:
            try:
                self.run('test -f %s' % path)
                logging.debug("Found remote path %s" % path)
                return path
            except:
                logging.debug("Remote path %s is missing", path)

        return None

    def job_start(self):
        """
        abstract method, when the remote host object is created
        and a job on it starts, it will be called
        """
        messages_file = self._var_log_messages_path()
        if messages_file is not None:
            try:
                self.run('rm -fr %s' % self.VAR_LOG_MESSAGES_COPY_PATH)
                self.run('cp %s %s' % (messages_file,
                            self.VAR_LOG_MESSAGES_COPY_PATH))
            except Exception, e:
                logging.info('Failed to copy %s at startup: %s',
                                messages_file, e)
        else:
            logging.debug("No remote messages path found, looked %s",
                            self.VAR_LOG_MESSAGES_COPY_PATH)

    def get_autodir(self):
        return self.autodir

    def set_autodir(self, autodir):
        """
        this method is called to make the host object aware of where to
        install the Caliper.
        """
        self.autodir = autodir

    def sysrq_reboot(self):
        self.run('echo b > /proc/sysrq-trigger &')

    def get_tmp_dir(self, parent='/tmp'):
        """
        return the pathname of a directory on the host suitable
        for temporary file storage
        The directory and its content will be deleted automaticallu on the
        destruction of the Host object that was used to obtain it.
        """
        self.run("mkdir -p %s" % parent)
        template = os.path.join(parent, 'caliper-XXXXXX')
        dir_name = self.run("mktemp -d %s" % template).stdout.rstrip()
        self.tmp_dirs.append(dir_name)
        return dir_name

    def get_platform_label(self):
        """
        Return the platform label, or None if platform label is not set.
        """
        if self.job:
            keyval_path = os.path.join(self.job.resultdir, 'host_keyvals',
                                        self.hostname)
            keyvals = utils.read_keyval(keyval_path)
            return keyvals.get('platform', None)
        else:
            return None

    def get_all_labels(self):
        """
        Return all labels, or empty list if label is not set
        """
        if self.job:
            keyval_path = os.path.join(self.job.resultdir, 'host_keyvals',
                                        self.hostname)
            keyvals = utils.read_keyval(keyval_path)
            all_labels = keyvals.get('labels', '')
            if all_labels:
                all_labels = all_labels.split(',')
                return [urllib.unquote(label) for label in all_labels]
        return []

    def delete_tmp_dir(self, tmpdir):
        """
        delete the given temporary directory on the remote machine
        """
        self.run('rm -fr "%s"' % utils.sh_escape(tmpdir), ignore_status=True)
        self.tmp_dirs.remove(tmpdir)

    def check_uptime(self):
        """
        Check that uptime is available and monotonically increasing
        """

        if not self.is_up():
            raise error.ServHostError('Client does not appear to be up')
        result = self.run("/bin/cat /proc/uptime", 30)
        return result.stdout.strip().split()[0]
