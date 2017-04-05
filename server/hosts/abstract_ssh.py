#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
import tempfile
import socket
import glob
import shutil

from caliper.client.shared import error, autotemp
from caliper.server import utils
from caliper.server.hosts import remote_host
from caliper.client.shared.settings import settings


enable_master_ssh = settings.get_value('TestNode', 'enable_master_ssh',
                                        type=bool, default=False)


def _make_ssh_cmd_default(user="root", port=22, opts='',
                            hosts_file='/dev/null', connect_timeout=30,
                            alive_interval=300):
    base_command = ("/usr/bin/ssh -a -x %s -o StrictHostKeyChecking=no "
                    "-o UserKnownHostsFile=%s -o BatchMode=yes "
                    "-o ConnectTimeout=%d -o ServerAliveInterval=%d "
                    "-l %s -p %d")
    assert isinstance(connect_timeout, (int, long))
    assert connect_timeout > 0
    if isinstance(port, str):
        port = int(port)
    return base_command % (opts, hosts_file,
                            connect_timeout, alive_interval, user, port)


class AbstractSSHHost(remote_host.RemoteHost):

    def _initialize(self, hostname, user="root", port=22, password="", *args,
                    **dargs):
        super(AbstractSSHHost, self)._initialize(hostname=hostname, *args,
                **dargs)
        self.ip = socket.getaddrinfo(self.hostname, None)[0][4][0]
        self.user = user
        self.port = port
        self.password = password
        self._use_rsync = None
        self.known_hosts_file = tempfile.mkstemp()[1]
        """
        master SSH connection backgroud job, socket temp directory and socket
        control path option. if master-ssh is enabled, these fields will be
        initialized by start_master_ssh when a new SSH connection is initialed
        """
        self.master_ssh_job = None
        self.master_ssh_tempdir = None
        self.master_ssh_option = ''

    def use_rsync(self):
        if self._use_rsync is not None:
            return self._use_rsync

        # check if the rsync is available on the remote host. If it's not,
        # don't try to use it for any future file transfers.
        self._use_rsync = self._check_rsync()
        if not self._use_rsync:
            logging.warn("rsync not available on remote host %s -- disabled",
                            self.hostname)
        return self._use_rsync

    def _check_rsync(self):
        try:
            self.run("rsync --version", stdout_tee=None, stderr_tee=None)
        except error.ServRunError:
            return False
        return True

    def _make_rsync_cmd(self, sources, dest, delete_dest, preserve_symlinks):
        """
        given a list of file paths, encodes it as a single remote path,
        in the style used by rsync and scp
        """
        ssh_cmd = _make_ssh_cmd_default(user=self.user, port=self.port,
                                        opts=self.master_ssh_option,
                                        hosts_file=self.known_hosts_file)
        if delete_dest:
            delete_flag = "--delete"
        else:
            delete_flag = ""
        if preserve_symlinks:
            symlink_flag = ""
        else:
            symlink_flag = "-L"
        command = "rsync %s %s --timeout=1800 --rsh='%s' -az %s %s"
        return command % (symlink_flag, delete_flag, ssh_cmd,
                        " ".join(sources), dest)

    def _make_rsync_compatible_globs(self, path, is_local):
        """
        given an rsync-style path, returns a list of globbed paths that will
        hopefully provide equivalent behaviour for scp. Does not support the
        full range of rsync pattern matching behaviour, only that exposed in
        the get/send_file interface.
        """
        if len(path) == 0 or path[-1] != "/":
            return [path]

        if is_local:
            def glob_matches_files(path, pattern):
                return len(glob.glob(path + pattern)) > 0
        else:
            def glob_matches_files(path, pattern):
                result = self.run("ls \"%s\"%s" %
                            (utils.sh_escape(path), pattern),
                            stdout_tee=None, ignore_status=True)
                return result.exit_status == 0
        patterns = ["*", ".[!.]*"]
        patterns = [p for p in patterns if glob_matches_files(path, p)]

        # convert them into a set of paths suitable for the commandline
        if is_local:
            return ["\"%s\"%s" % (utils.sh_escape(path), pattern)
                    for pattern in patterns]
        else:
            return [utils.scp_remote_escape(path) + pattern
                    for pattern in patterns]

    def _make_rsync_compatible_source(self, source, is_local):
        """
        Applies the same logic as _make_rsync_ccompatible_globs, but applies if
        to an entire list of sources, producing a new list of sources,
        properly quoted.
        """
        return sum((self._make_rsync_compatible_globs(path, is_local)
                    for path in source), [])

    def _encode_remote_paths(self, paths, escape=True):
        """
        Given a list of file paths, encodes it as a single remote path, in the
        style used by rsync and scp.
        """
        if escape:
            paths = [utils.scp_remote_escape(path) for path in paths]
        return '%s@%s:"%s"' % (self.user, self.hostname, " ".join(paths))

    def _make_ssh_cmd(self, cmd):
        base_cmd = _make_ssh_cmd_default(user=self.user, port=self.port,
                                    opts=self.master_ssh_option,
                                    hosts_file=self.known_hosts_file)
        return '%s %s "%s"' % (base_cmd, self.hostname, utils.sh_escape(cmd))

    def _make_scp_cmd(self, sources, dest):
        """
        Given a list of source paths and a destination path, produces the
        appropriate scp command for encoding it. Remote paths must be
        pre-encoded.
        """
        command = ("scp -rq %s -o StrictHostKeyChecking=no -o "
                    "UserKnownHostsFile=%s -P %d %s '%s'")
        return command % (self.master_ssh_option, self.known_hosts_file,
                            self.port, " ".join(sources), dest)

    def _set_umask_perms(self, dest):
        """
        Given a destination file/dir (recursively) set the permissions on all
        the files and directories to the max allowed by running umask.
        """
        umask = os.umask(0)
        os.umask(umask)

        max_privs = 0777 & ~umask

        def set_file_privs(filename):
            file_stat = os.stat(filename)
            file_privs = max_privs
            # if the original file permissions do not have at least one
            # executable bit then do not set it anywhere
            if not file_stat.st_mode & 0111:
                file_privs &= ~0111

            os.chmod(filename, file_privs)
        for root, dirs, files in os.walk(dest, topdown=False):
            for dirname in dirs:
                os.chmod(os.path.join(root, dirname), max_privs)
            for filename in files:
                set_file_privs(os.path.join(root, filename))

        if os.path.isdir(dest):
            os.chmod(dest, max_privs)
        else:
            set_file_privs(dest)

    def get_file(self, source, dest, delete_dest=False, preserve_perm=True,
                preserve_symlinks=False):
        """
        Copy files from the remote host to a local path
        Directories will be copied recursively.
        Args:
            delete_dest: if it is true, the command will also clear out any
                        old files at dest that are not in the source
            preserve_perm: tells get_file() to try to preserve the sources
                            permissions on files and dirs
            preserve_symlinks: try to preserver symlinks instead of
                            transforming them into files/dirs on copy
        Raiseds:
            the scp command failed
        """
        self.start_master_ssh()
        if isinstance(source, basestring):
            source = [source]
        dest = os.path.abspath(dest)

        try_scp = True
        if try_scp:
            if delete_dest and os.path.isdir(dest):
                shutil.rmtree(dest)
                os.mkdir(dest)

            remote_source = self._make_rsync_compatible_source(source, False)
            if remote_source:
                remote_source = self._encode_remote_paths(remote_source,
                                                escape=False)
                local_dest = utils.sh_escape(dest)
                scp = self._make_scp_cmd([remote_source], local_dest)
                try:
                    utils.run(scp)
                except error.CmdError, e:
                    raise error.ServeRunError(e.args[0], e.args[1])

        if not preserve_perm:
            # have no way to tell scp to not try to preserve the permssions so
            # set them after copy instead.
            # for rsync we could use "--no-p --chmod=ugo-rmX" but those
            # options are only in veryrecent rsync versions
            self._set_umask_perms = (dest)

    def send_file(self, source, dest, delete_dest=False,
            preserve_symlinks=False):
        """
        Copy files from a local path to the remote host.
        """
        self.start_master_ssh()

        if isinstance(source, basestring):
            source_is_dir = os.path.isdir(source)
            source = [source]
        remote_dest = self._encode_remote_paths([dest])

        # if rsync is diabled or fails, try scp
        try_scp = True

        if try_scp:
            # scp has no equivalent to --delete, just drop the entire dest dir
            if delete_dest:
                dest_exists = False
                try:
                    self.run("test -x %s" % dest)
                    dest_exists = True
                except error.ServRunError:
                    pass

                dest_is_dir = False
                if dest_exists:
                    try:
                        self.run("test -d %s" % dest)
                        dest_is_dir = True
                    except error.ServRunError:
                        pass

                # if there is a list of more than one path, destination *has*
                # to be a dir.It therr's a single path being transferred and
                # it is a dir, the destination also has to be a dir
                if len(source) > 1 and source_is_dir:
                    dest_is_dir = True

                if dest_exists and dest_is_dir:
                    cmd = "rm -fr %s && mkdir %s" % (dest, dest)
                elif not dest_exists and dest_is_dir:
                    cmd = "mkdir %s" % dest
                    self.run(cmd)

            local_sources = self._make_rsync_compatible_source(source, True)
            if local_sources:
                scp = self._make_scp_cmd(local_sources, remote_dest)
                try:
                    utils.run(scp)   # utils.run
                except error.CmdError, e:
                    raise error.ServRunError(e.args[0], e.args[1])

    def ssh_ping(self, timeout=60):
        try:
            self.run("true", timeout=timeout, connect_timeout=timeout)
        except error.ServSSHTimeout:
            msg = "Host (ssh) verify timed out (timeout = %d)" % timeout
            raise error.ServSSHTimeout(msg)
        except error.ServSSHPermissionDeniedError:
            raise
        except error.ServRunError, e:
            raise error.ServSSHPingHostError(e.description + '\n' +
                    repr(e.result_obj))

    def is_up(self):
        """
        Check if the remote host is up.
        """
        try:
            self.ssh_ping()
        except error.ServRunError:
            return False
        else:
            return True

    def verify_connectivity(self):
        super(AbstractSSHHost, self).verify_connectivity()
        logging.info('pinging host ' + self.hostname)
        self.ssh_ping()
        logging.info("Host (ssh) %s is alive", self.hostname)

        if self.is_shutting_down():
            raise error.ServHostIsShuttingDownError("Host is shutting down")

    def close(self):
        super(AbstractSSHHost, self).close()
        self._cleanup_master_ssh()
        os.remove(self.known_hosts_file)

    def _cleanup_master_ssh(self):
        """
        Release all resources (process, temporary directory) used by an active
        master SSH connection.
        """
        if self.master_ssh_job is not None:
            # utils.nuke_subprocess
            utils.nuke_subprocess(self.master_ssh_job.sp)
            self.master_ssh_job = None

        # remove the temporary directory for the master SSH socket
        if self.master_ssh_tempdir is not None:
            self.master_ssh_tempdir.clean()
            self.master_ssh_tmepdir = None
            self.master_ssh_option = ''

    def start_master_ssh(self):
        """
        Called whenever a slave SSH connection needs to be intiated.
        If the master SSH support is enabled and a master SSH connection is not
        active already, start a new one in the backgroud.
        """
        if not enable_master_ssh:
            return

        # if a previously started master SSH connection is not running anymore
        # it needs to be cleaned up and then restarted.
        if self.master_ssh_job is not None:
            if self.master_ssh_job.sp.poll() is not None:
                logging.info("Master ssh connection to %s is down.",
                        self.hostname)
                self._cleanup_master_ssh()

        # start a new master SSH connection
        if self.master_ssh_job is None:
            # create a shared socket in a temp location.

            self.master_ssh_tempdir = autotemp.tempdir(unique_id='ssh-master')
            self.master_ssh_option = ("-o ControlPath=%s/socket" %
                                        self.master_ssh_tempdir.name)
            # start the master SSh connection in the backgroud.
            master_cmd = self.ssh_command(options="-N -o ControlMaster=yes")
            logging.debug("Starting master ssh connection '%s'" % master_cmd)
            self.master_ssh_job = utils.BgJob(master_cmd)  # To change

    def clear_known_hosts(self):
        logging.info("Clearing known hosts for host '%s', file '%s'.",
                        self.hostname, self.known_hosts_file)
        # clear out the file by opening if for writing and then closing
        fh = open(self.known_hosts_file, 'w')
        fh.close()
