#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import subprocess
import re

from caliper.client.shared import error, ssh_key
from caliper.server import utils
from caliper.server.hosts import abstract_ssh

_TEMPLATE = '_autotmp'

# def temp_dir(self, suffix='', unique_id=None, prefix='', dir=None):
#    suffix = unique_fis + suffix
#    prefix = prefix + _TEMPLATE
#    return module_tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)


class SSHHost(abstract_ssh.AbstractSSHHost):
    """
    This class represents a remote machine controlled through an ssh
    session on which you can run programs.

    The machine must be configured for password-less login, for example
    through public key authentication.

    It includes support for controlling the machine through a serial console
    on which you can run programs.
    """
    def _initialize(self, hostname, *args, **dargs):
        """
        Construct a SSHHost object
        Args:
            hostname: network hostname or address of remote machine
        """
        super(SSHHost, self)._initialize(hostname=hostname, *args, **dargs)
        self.setup_ssh()

    def ssh_command(self, connect_timeout=30, options='', alive_interval=300):
        """
        Construct an ssh command with proper args for this host.
        """
        options = "%s %s" % (options, self.master_ssh_option)
        base_cmd = abstract_ssh._make_ssh_cmd_default(user=self.user,
                                        port=self.port, opts=options,
                                        hosts_file=self.known_hosts_file,
                                        connect_timeout=connect_timeout,
                                        alive_interval=alive_interval)
        return "%s %s" % (base_cmd, self.hostname)

    def _run(self, command, timeout, ignore_status, stdout, stderr,
                connect_timeout, env, options, stdin, args):
        """Helper function for run"""
        ssh_cmd = self.ssh_command(connect_timeout, options)
        if not env.strip():
            env = ""
        else:
            env = "export %s;" % env

        for arg in args:
            command += ' "%s"' % utils.sh_escape(arg)

        full_cmd = '%s "%s %s"' % (ssh_cmd, env, utils.sh_escape(command))
        result = utils.run(full_cmd, timeout, True, stdout, stderr,
                            verbose=False, stdin=stdin,
                            stderr_is_expected=ignore_status)
        # the error message will show up in band(indistinguishable from stuff
        # sent through the SSH connection). so we hace the remote computer
        # echo the message "Connected." before running any command.
        if result.exit_status == 255:
            if re.search(r'^ssh: connect to the host .* port .*: '
                         r'Connection timed out\r$', result.stderr):
                raise error.ServSSHTimeour("ssh timed out", result)
            if "Permission Denied." in result.stderr:
                msg = "ssh permission denied"
                raise error.ServSSHPemissionDenidError(msg, result)

        if not ignore_status and result.exit_status > 0:
            raise error.ServRunError("command execution error", result)

        return result
    #FIXME what should be the ideal timeout value ?
    def run(self, command, timeout=14400, ignore_status=False,
            stdout_tee=utils.TEE_TO_LOGS,
            stderr_tee=utils.TEE_TO_LOGS, connect_timeout=30, options='',
            stdin=None, verbose=True, args=()):
        """
        run a command on the remote host
        """
        if verbose:
            logging.debug("Running (ssh) '%s'" % command)
        self.start_master_ssh()
        env = " ".join("=".join(pair) for pair in self.env.iteritems())
        try:
            return self._run(command, timeout, ignore_status, stdout_tee,
                                stderr_tee, connect_timeout, env, options,
                                stdin, args)
        except error.CmdError, cmderr:
            raise error.ServRunError(cmderr.args[0], cmderr.args[1])

    def setup_ssh(self):
        if self.password:
            try:
                self.ssh_ping()
            except error.ServSSHPingHostError:
                ssh_key.setup_ssh_key(self.hostname, self.user, self.password,
                                        self.port)


class AsyncSSHMixin(object):
    def __init__(self, *args, **dargs):
        super(AsyncSSHMixin, self).__init__(*args, **dargs)

    def run_async(self, command, stdout_tee=None, stderr_tee=None, args=(),
                    connect_timeout=30, options='', verbose=True,
                    stderr_level=utils.DEFAULT_STDERR_LEVEL,
                    cmd_outside_subshell=''):
        """
        Run a command on the remote host. Return an AsyncJob object to
        interact with the remote process.
        """
        if verbose:
            logging.debug("Running (async ssh) '%s'" % command)

        # start a master SSH connection if necessary
        self.start_master_ssh()

        self.send_file(os.path.join(self.job.clientdir, "shared", "hosts",
                                        "scripts", "run_helper.py"),
                        os.path.join(self.job.tmpdir, "run_helper.py"))

        env = " ".join("=".join(pair) for pair in self.env.iteritems())
        ssh_cmd = self.ssh_command(connect_timeout, options)
        if not env.strip():
            env = ""
        else:
            env = "export %s;" % env

        for arg in args:
            command += ' "%s"' % utils.sh_escape(arg)
        full_cmd = '{ssh_cmd} "{env} {cmd}"'.format(ssh_cmd=ssh_cmd, env=env,
                cmd=utils.sh_escape("%s (%s '%s')" % (cmd_outside_subshell,
                                os.path.join(self.job.tmpdir, "run_helper.py"),
                                utils.sh_escape(command))))
        job = utils.AsyncJob(full_cmd, stdout_tee=stdout_tee,
                                stderr_tee=stderr_tee, verbose=verbose,
                                stderr_level=stderr_level,
                                stdin=subprocess.PIPE)

        def kill_func():
            utils.nuke_subprocess(job.sp)

        job.kill_func = kill_func

        return job
