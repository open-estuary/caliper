
# -*- coding:utf-8 -*-
#
#   Date    :   15/01/04 16:32:44
#   Desc    :
#
from __future__ import print_function
import os
import random
import select
import shutil
import subprocess
import signal
import StringIO
import time
import re
import textwrap
import logging
from threading import Thread, Lock
import commands
import string
import ConfigParser
import fcntl
import errno

from caliper.client.shared import error, logging_manager
from caliper.client.shared.settings import settings
from caliper.client.shared import caliper_path
from caliper.client.shared.tests_setting import BaseCfg


class SimpleFlock:
   def __init__(self, path, timeout = None):
      self._path = path
      self._timeout = timeout
      self._fd = None

   def __enter__(self):
      self._fd = os.open(self._path,os.O_CREAT)
      start_lock_search = time.time()
      while True:
         try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Lock acquired!
            return self._fd
         except (OSError, IOError) as ex:
            if ex.errno != errno.EAGAIN: # Resource temporarily unavailable
               print(ex)
               raise
            elif self._timeout is not None and time.time() > (start_lock_search + self._timeout):
               # Exceeded the user-specified timeout.
               print("TIMEOUT")
               raise
         time.sleep(0.1)

   def __exit__(self, *args):
      fcntl.flock(self._fd, fcntl.LOCK_UN)
      os.close(self._fd)
      self._fd = None

class _NullStream(object):
    def write(self, data):
        pass

    def flush(self):
        pass

TEE_TO_LOGS = object()
_the_null_stream = _NullStream()

DEFAULT_STDOUT_LEVEL = logging.DEBUG
DEFAULT_STDERR_LEVEL = logging.ERROR

STDOUT_PREFIX = '[stdout]'
STDERR_PREFIX = '[stderr]'


def file_copy(des_file, source_file, style):
    des_fp = open(des_file, style)
    source_fp = open(source_file, 'r')
    content = source_fp.read()
    des_fp.write(content)
    source_fp.close()
    des_fp.close()


def read_config_file(filename):
    config = ConfigParser.ConfigParser()
    config.read(filename)
    sections = config.sections()
    return (config, sections)


def get_local_ip():
    cmd_output = commands.getoutput('ifconfig')
    obtain_ip = re.findall('inet addr:(\d+\.\d+\.\d+\.\d+)', cmd_output)
    if obtain_ip:
        return obtain_ip
    else:
        return ['127.0.1.1']


"""
For 'android', we read 'common_cases_def.cfg' and 'common_case_def.cfg';
For 'arm', read the 'common_case_def.cfg' and 'arm_cases_def.cfg';
For 'x86', read the 'common_case_def.cfg' and 'server_cases_def.cfg'.
"""
def get_cases_def_files(option):
    cfg_files = []
    cases_tail = "_cases_def.cfg"

    common_cfg = "common" + cases_tail
    common_cfg_path = os.path.join(caliper_path.config_files.tests_cfg_dir,
                                    common_cfg)
    cfg_files.append(common_cfg_path)

    application_cfg = "application" + cases_tail
    application_cfg_path = os.path.join(caliper_path.config_files.tests_cfg_dir,
                                        application_cfg)
    cfg_files.append(application_cfg_path)

    if (option == 'arm_32'):
        other_cfg = "arm" + cases_tail
    elif (option == 'android'):
        other_cfg = "android" + cases_tail
    elif (option == 'arm_64'):
        other_cfg = "server" + cases_tail
    else:
        other_cfg = 'server' + cases_tail
    other_cfg_path = os.path.join(caliper_path.config_files.tests_cfg_dir,
                                    other_cfg)
    cfg_files.append(other_cfg_path)
    return cfg_files


def get_config_value(config_name, section, key):
    cfg_file = os.path.join(caliper_path.config_files.config_dir, config_name)
    try:
        cfg = BaseCfg(cfg_file)
        value = cfg.get_value(section, key)
    except Exception:
        raise
    else:
        return value


def get_fault_tolerance_config(section, key):
    flag = 0
    logging.debug(caliper_path.config_files.config_dir)
    cfg_file = os.path.join(caliper_path.config_files.config_dir,
                                    'execution_contl.cfg')
    try:
        tolerence_cfg = BaseCfg(cfg_file)
        value = tolerence_cfg.get_value(section, key)
    except Exception:
        raise
    else:
        if (value.startswith("True") or value.startswith("true")):
            flag = 1
        elif (value.startswith("False") or value.startswith('false')):
            flag = 0
        elif value == '':
            flag = 1
        else:
            logging.info("Wrong configuration in config/execution_contl.cfg")
            flag = 0
        return flag


def get_server_cfg_path(bench_name):
    bench_cfg_location = os.path.join(caliper_path.config_files.tests_cfg_dir,
                                        bench_name)
    server_config_file = ''
    for root, dirs, files in os.walk(os.path.abspath(bench_cfg_location)):
        for i in range(0, len(files)):
            if re.search('server', files[i]):
                server_config_file = os.path.join(root, files[i])
                break
            if re.search('application', files[i]):
                server_config_file = os.path.join(root, files[i])
                break

    return server_config_file

def get_application_cfg_path(bench_name):
    bench_cfg_location = os.path.join(caliper_path.config_files.tests_cfg_dir,
                                        bench_name)
    application_config_file = ''
    for root, dirs, files in os.walk(os.path.abspath(bench_cfg_location)):
        for i in range(0, len(files)):
            if re.search('application', files[i]):
                application_config_file = os.path.join(root, files[i])
                break
    return application_config_file

def get_stream_tee_file(stream, level, prefix=''):
    if stream is None:
        return _the_null_stream
    if stream is TEE_TO_LOGS:
        return logging_manager.LoggingFile(level=level, prefix=prefix)
    return stream


class BgJob(object):
    def __init__(self, command, stdout_tee=None, stderr_tee=None,
                    verbose=True, stdin=None,
                    stderr_level=DEFAULT_STDERR_LEVEL, close_fds=False):
        self.command = command
        self.stdout_tee = get_stream_tee_file(stdout_tee,
                                                DEFAULT_STDOUT_LEVEL,
                                                prefix=STDOUT_PREFIX)
        self.stderr_tee = get_stream_tee_file(stderr_tee, stderr_level,
                                                prefix=STDERR_PREFIX)
        # need to be changed
        self.result = CmdResult(command)
        # allow for easy stdin input by string, we'll let subprocess create a
        # pipe for stdin input and we'll write to it in the wait loop
        if isinstance(stdin, basestring):
            self.string_stdin = stdin
            stdin = subprocess.PIPE
        else:
            self.string_stdin = None

        if verbose:
            logging.debug("Running '%s'" % command)

        shell = '/bin/bash'
        if not os.path.isfile(shell):
            shell = '/bin/sh'
        self.sp = subprocess.Popen(command, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    preexec_fn=self._reset_sigpipe,
                                    close_fds=close_fds,
                                    shell=True, executable=shell,
                                    stdin=stdin)

    def output_prepare(self, stdout_file=None, stderr_file=None):
        self.stdout_file = stdout_file
        self.stderr_file = stderr_file

    def process_output(self, stdout=True, final_read=False):
        """output_prepare must be called before calling this function"""
        if stdout:
            pipe, buf, tee = self.sp.stdout, self.stdout_file, self.stdout_tee
        else:
            pipe, buf, tee = self.sp.stderr, self.stderr_file, self.stderr_tee

        if final_read:
            # read in all the data we can from pipe and then stop
            data = []
            while select.select([pipe], [], [], 0)[0]:
                data.append(os.read(pipe.fileno(), 1024))
                if len(data[-1]) == 0:
                    break
            data = "".join(data)
        else:
            # perform a single read
            data = os.read(pipe.fileno(), 1024)
        buf.write(data)
        tee.write(data)

    def cleanup(self):
        self.stdout_tee.flush()
        self.stderr_tee.flush()
        self.sp.stdout.close()
        self.sp.stderr.close()
        self.result.stdout = self.stdout_file.getvalue()
        self.result.stderr = self.stderr_file.getvalue()

    def _reset_sigpipe(self):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)


class AsyncJob(BgJob):
    def __init__(self, command, stdout_tee=None, stderr_tee=None,
                    verbose=True, stdin=None,
                    stderr_level=DEFAULT_STDERR_LEVEL,
                    kill_func=None, close_fds=False):
        super(AsyncJob, self).__init__(command, stdout_tee=stdout_tee,
                                        stderr_tee=stderr_tee,
                                        verbose=verbose, stdin=stdin,
                                        stderr_level=stderr_level,
                                        close_fds=close_fds)
        self.start_time = time.time()
        if kill_func is None:
            self.kill_func = self._kill_self_process
        else:
            self.kill_func = kill_func

        if self.string_stdin:
            self.stdin_lock = Lock()
            string_stdin = self.string_stdin
            # replace with None so that _wait_for_commands will nor try to
            # re-write it
            self.string_stdin = None
            self.stdin_thread = Thread(
                    target=AsyncJob._stdin_string_drainer,
                    name=("%s-stdin" % command),
                    args=(string_stdin, self.sp.stdin)
                    )
            self.stdin_thread.daemon = True
            self.stdin_thread.start()

        self.stdout_lock = Lock()
        self.stdout_file = StringIO.StringIO()
        self.stdout_thread = Thread(
                target=AsyncJob._fd_drainer,
                name=("%s-stdout" % command),
                args=(
                    self.sp.stdout,
                    [self.stdout_file, self.stdout_tee],
                    self.stdout_lock
                    )
                )
        self.stdout_thread.daemon = True

        self.stderr_lock = Lock()
        self.stderr_file = StringIO.StringIO()
        self.stderr_thread = Thread(
                target=AsyncJob._fd_drainer,
                name=("%s-stderr" % command),
                args=(
                    self.sp.stderr,
                    [self.stderr_file, self.stderr_tee],
                    self.stderr_lock
                    )
                )
        self.stderr_thread.daemon = True

        self.stdout_thread.start()
        self.stderr_thread.start()

    @staticmethod
    def _stdin_string_drainer(input_string, stdin_pipe):
        """
        input is a string and output is PIPE
        """
        try:
            while True:
                # we can write PIPE_BUF bytes without blocking after a poll or
                # select we aren't doing either but let's small chunks anyway.
                # POSIX requires PIPE_BUF >= 512
                # 512 should be repalced with select.PIPE_BUF in Python 2.7+
                tmp = input_string[:512]
                if tmp == '':
                    break

                stdin_pipe.write(tmp)
                input_string = input_string[512:]
        finally:
            # close reading PIPE so that the reader doesn't block
            stdin_pipe.close()

    @staticmethod
    def _fs_drainer(input_pipe, outputs, lock):
        """
        input is a pipe and output is file-like. If lock is non-None, then we
        assume output is not thread-safe
        """
        # if we don't have a lock object, then call a noop function like bool
        acquire = getattr(lock, 'acquire', bool)
        release = getattr(lock, 'release', bool)
        writable_objs = [obj for obj in outputs if hasattr(obj, 'write')]
        fileno = input_pipe.fileno()
        while True:
            # 1024 because that's what we did before
            tmp = os.read(fileno, 1024)
            if tmp == '':
                break
            acquire()
            try:
                for f in writable_objs:
                    f.write(tmp)
            finally:
                release()
        # don't close writeable_objs, the callee will close

    def output_prepare(self, stdout_file=None, stderr_file=None):
        raise NotImplementedError("This onject automatically prepares its"
                                    " own output")

    def process_output(self, stdout=True, final_read=False):
        raise NotImplementedError("This object has backgroud threads"
                                    "automatically polling "
                                    "the process. Use the locked accessors")

    def get_stdout(self):
        self.stdout_lock.acquire()
        tmp = self.stdout_file.getvalue()
        self.stdout_lock.release()
        return tmp

    def get_stderr(self):
        self.stderr_lock.acquire()
        tmp = self.stderr_file.getvalue()
        self.stderr_lock.release()
        return tmp

    def cleanup(self):
        raise NotImplementedError("This must be waited for to get a result")

    def _kill_self_process(self):
        try:
            os.kill(self.sp.pid, signal.SIGTERM)
        except OSError:
            pass

    def wait_for(self, timeout=None):
        """
        wait for the process to finish, process is safely destroyes after
        timeout.
        """
        if timeout is None:
            self.sp.wait()

        if timeout > 0:
            start_time = time.time()
            while time.time() - start_time < timeout:
                self.result.exit_status = self.sp.poll()
                if self.result.exit_status is not None:
                    break
        else:
            timeout = 1
            # first need to kill the the threads and process, then no more
            # locking issues for superclass's cleanup function
        self.kill_func()
        # verify it was really killed with provided kill function
        stop_time = time.time() + timeout
        while time.time() < stop_time:
            self.result.exit_status = self.sp.poll()
            if self.result.exit_status is not None:
                break
        else:
            # process is immune against self.kill_func() use 9
            try:
                os.kill(self.sp.pid, signal.SIGKILL)
            except OSError:
                pass
                # don't care if the process is already gone
        # we need to fill in parts of the result that aren't done
        # automatically
        try:
            _, self.result.exit_status = os.waitpid(self.sp.pid, 0)
        except OSError:
            self.result.exit_status = self.sp.poll()
        self.result.duration = time.time() - self.start_time
        assert self.result.exit_status is not None

        # make sure we've got sdtout and stderr
        self.stdout_thread.join(1)
        self.stderr_thread.join(1)
        assert not self.stdout_thread.isAlive()
        assert not self.stderr_thread.isAlive()

        super(AsyncJob, self).cleanup()
        return self.result


def get_stderr_level(stderr_is_expected):
    if stderr_is_expected:
        return DEFAULT_STDOUT_LEVEL
    return DEFAULT_STDERR_LEVEL


class CmdResult(object):
    """
    Command execution result.
    """
    def __init__(self, command="", stdout="", stderr="", exit_status=None,
                        duration=0):
        self.command = command
        self.exit_status = exit_status
        self.stdout = stdout
        self.stderr = stderr
        self.duration = duration

    def __repr__(self):
        wrapper = textwrap.TextWrapper(width=78, initial_indent="\n     ",
                                        subsequent_indent="     ")
        stdout = self.stdout.rstrip()
        if stdout:
            stdout = "\nstdout:\n%s" % stdout

        stderr = self.stderr.rstrip()
        if stderr:
            stderr = "\nstderr:\n%s" % stderr

        return ("* Command: %s\n"
                "Exit_status: %s\n"
                "Duration: %s\n"
                "%s"
                "%s"
                % (wrapper.fill(self.command), self.exit_status,
                    self.duration, stdout, stderr))


def get_children_pids(ppid):
    """
    get all PIDs of children/threads pf parent ppid
    """
    return (system_output("ps -L --ppid=%d -l lwp" % ppid).split('\n')[1:])


def pid_is_alive(pid):
    """
    True if process pid exists and is not yet stuck in Zombie status.
    """
    path = '/proc/%s/stat ' % pid
    try:
        stat = read_one_line(path)
    except IOError:
        if not os.path.exists(path):
            return False
        raise
    return stat.split()[2] != 'Z'


def signal_pid(pid, sig):
    """
    send a signal to a process id, return True if the process terminated
    successfully
    """
    try:
        os.kill(pid, sig)
    except OSError:
        # the process may have died before we kill it
        pass
    for i in range(5):
        if not pid_is_alive(pid):
            return True
        time.sleep(1)


def nuke_subprocess(subproc):
    # first, check if the subprocess is still alive
    if subproc.poll() is not None:
        return subproc.poll()

    # if the time exceed the timeout, then terminated it
    signal_queue = [signal.SIGTERM, signal.SIGKILL]
    for sig in signal_queue:
        signal_pid(subproc.pid, sig)
        if subproc.poll() is not None:
            return subproc.poll()


def nuke_pid(pid, signal_queue=(signal.SIGTERM, signal.SIGKILL)):
    for sig in signal_queue:
        if signal_pid(pid, sig):
            return
    raise error.ServRunError("Could not kill %d" % pid, None)


def kill_process_tree(pid, sig=signal.SIGKILL):
    """
    signal a process and all of its children

    if the process does not exist -- return
    """
    if not safe_kill(pid, signal.SIGSTOP):
        return
    children = commands.getoutput("ps --ppid=%d -o pid=" % pid).split()
    for child in children:
        kill_process_tree(int(child), sig)
    safe_kill(pid, sig)
    safe_kill(pid, signal.SIGCONT)


def close_log_file(filename):
    global _open_log_files, _log_file_dir
    remove = []
    for k in _open_log_files:
        if os.path.basename(k) == filename:
            f = _open_log_files[k]
            f.close()
            remove.append(k)
    if remove:
        for key_to_remove in remove:
            _open_log_files.pop(key_to_remove)


def safe_kill(pid, signal):
    """
    Attempt to send a signal to a given process that may or may not exist.
    """
    try:
        os.kill(pid, signal)
        return True
    except Exception:
        return False


def read_file(filename):
    f = open(filename)
    try:
        return f.read()
    finally:
        f.close()


def read_one_line(filename):
    return open(filename, 'r').readline().rstrip('\n')


def pid_exists(pid):
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def get_process_name(pid):
    """
    get process name from PID
    """
    return get_field(read_file("/proc/%d/stat" % pid), 1)[1:-1]


def get_field(data, param, linestart="", sep=" "):
    """
    parser data from string
    """
    search = re.compile(r"(?<=^%s)\s*(.*)" % linestart, re.MULTILINE)
    find = search.search(data)
    if find is not None:
        return re.split("%s" % sep, find.group(1))[param]
    else:
        logging.info("There is no line which starts with {} in data." %(linestart))
        return None


def program_is_alive(program_name, pid_files_dir=None):
    """
    checks if the progress is alive and not in Zombie state.
    """
    pid = get_pid_from_file(program_name, pid_files_dir)
    if pid is not None:
        return False
    return pid_is_alive(pid)


def get_pid_from_file(program_name, pid_files_dir=None):
    """
    Read the pid from <program_name>.pid
    """
    pid_file_path = get_pid_path(program_name, pid_files_dir)
    if not os.path.exists(pid_file_path):
        return None
    pidfile = open(get_pid_path(program_name, pid_files_dir), 'r')
    try:
        try:
            pid = int(pidfile.readline())
        except IOError:
            if not os.path.exists(pid_file_path):
                return None
        raise
    finally:
        pidfile.close()

    return pid


def get_pid_path(program_name, pid_files_dir=None):
    if pid_files_dir is None:
        pid_files_dir = settings.get_value("TestNode", "pid_files_dir",
                                            default="")

    if not pid_files_dir:
        base_dir = os.path.dirname(__file__)
        pid_path = os.path.abspath(os.path.join(base_dir, "...", "..",
                                    "%s.pid" % program_name))
    else:
        pid_path = os.path.join(pid_files_dir, "%s.pid" % program_name)

    return pid_path


def write_pid(program_name, pid_files_dir=None):
    """
    Try to drop <program_name>.pid in the directory
    """
    pidfile = open(get_pid_path(program_name, pid_files_dir), "w")
    try:
        pidfile.write("%s\n" % os.getpid())
    finally:
        pidfile.close()


def deletet_pid_file_if_exists(program_name, pid_files_dir=None):
    """
    try to remove <program_name>.pid from the directory
    """
    pidfile_path = get_pid_path(program_name, pid_files_dir)

    try:
        os.remove(pidfile_path)
    except OSError:
        if not os.path.exists(pidfile_path):
            return
        raise


def run(command, timeout=None, ignore_status=False, stdout_tee=None,
        stderr_tee=None, verbose=True, stdin=None, stderr_is_expected=None,
        args=()):
    """
    run a command on the host.
    :param stdout_tee: optional file-like object to which stdout data will be
                        written as it is generated (data will be stored in
                        result.stdout)
    :param stderr_tee: likewise for stderr
    :param verbose: if True, log the command being run
    :param args: sequence of strings of arguments to be given to the command
                    inside quotes after they have been escaped for that;
                    each element in the sequence will be given as a seperate
                    command argument
    :return: a CmdResult object
    :raise CmdError
    """
    if isinstance(args, basestring):
        raise TypeError('Got a string for the "args" keyword argument, "\
                        "need a sequence')

    for arg in args:
        command += '"%s"' % sh_escape(arg)
    if stderr_is_expected is None:
        stderr_is_expected = ignore_status

    bg_job = join_bg_jobs((BgJob(command, stdout_tee, stderr_tee,
                    verbose, stdin=stdin,
                    stderr_level=get_stderr_level(stderr_is_expected)),),
                    timeout)[0]
    if not ignore_status and bg_job.result.exit_status:
        raise error.CmdError(command, bg_job.result,
                                    "Command returned non-zero exit status")

    return bg_job.result


def generate_random_string(length, ignore_str=string.punctuation,
                                   convert_str=""):
    """
    Return a random string using alphanumeric characters.

    :param length: Length of the string that will be generated.
    :param ignore_str: Characters that will not include in generated string.
    :param convert_str: Characters that need to be escaped (prepend "\\").

    :return: The generated random string.
    """
    r = random.SystemRandom()
    str = ""
    chars = string.letters + string.digits + string.punctuation
    if not ignore_str:
        ignore_str = ""
    for i in ignore_str:
        chars = chars.replace(i, "")

    while length > 0:
        tmp = r.choice(chars)
        if convert_str and (tmp in convert_str):
            tmp = "\\%s" % tmp
        str += tmp
        length -= 1
    return str


def strip_console_codes(output):
    """
    Remove the Linux console escape and control sequences from the console
    output. Make the output readable and can be used for result check. Now
    only remove some basic console codes using during boot up.

    :param output: The output from Linux console
    :type output: string
    :return: the string wihout any special codes
    :rtype: string
    """
    if "\x1b" not in output:
        return output

    old_word = ""
    return_str = ""
    index = 0
    output = "\x1b[m%s" % output
    console_codes = "%G|\[m|\[[\d;]+[HJnrm]"
    while index < len(output):
        tmp_index = 0
        tmp_word = ""
        while (len(re.findall("\x1b", tmp_word)) < 2 and
                   index + tmp_index < len(output)):
            tmp_word += output[index + tmp_index]
            tmp_index += 1

        tmp_word = re.sub("\x1b", "", tmp_word)
        index += len(tmp_word) + 1
        if tmp_word == old_word:
            continue
        try:
            special_code = re.findall(console_codes, tmp_word)[0]
        except IndexError:
            if index + tmp_index < len(output):
                raise ValueError("%s is not included in the known console "
                                "codes list %s" % (tmp_word, console_codes))
                continue
        if special_code == tmp_word:
            continue
        old_word = tmp_word
        return_str += tmp_word[len(special_code):]
    return return_str


def process_or_children_is_defunct(ppid):
    """Verify if any processes from PPID is defunct.

    Attempt to verify if parent process and any children from PPID is defunct
    (zombie) or not.
    :param ppid: The parent PID of the process to verify.
    """
    defunct = False
    try:
        pids = get_children_pids(ppid)
    except error.CmdError:  # Process doesn't exist
        return True
    for pid in pids:
        cmd = "ps --no-headers -o cmd %d" % int(pid)
        proc_name = system_output(cmd, ignore_status=True)
        if '<defunct>' in proc_name:
            defunct = True
            break
    return defunct


def get_arch(run_function=run):
    """get the hardware architecture of the machine"""
    arch = run_function('/bin/uname -m').stdout.rstrip()
    if re.match(r'i\d86$', arch):
        arch = 'i386'
    return arch


def get_num_logical_cpus_per_socket(run_function=run):
    """
    get the number of cores (including hyperthreading) per cpu.
    run_function is used to execute the commands.
    """
    siblings = run_function('grep "^siblings" /proc/cpuinfo').stdout.rstrip()
    num_siblings = map(int, re.findall(r'^siblings\s*:\s*(\d+)\s*$',
                    siblings, re.M))

    if len(num_siblings) == 0:
        raise error.TestError('Unable to find siblings info in /proc/cpuinfo')
    if min(num_siblings) != max(num_siblings):
        raise error.TestError('Number of siblings differ %r' % num_siblings)

    return num_siblings[0]


def sh_escape(command):
    """
    escape special characters from a command so that it can be passed as a
    double quoted (" ") string in a (ba)sh command.
    """
    command = command.replace('\\', '\\\\')
    command = command.replace('$', r'\$')
    command = command.replace('"', r'\"')
    command = command.replace('`', r'\`')
    return command


def system_output(command, timeout=None, ignore_status=False,
        retain_output=False, args=(), verbose=True):
    """
    run a command and return the stdout output

    :param ignore_status: do not raise an exception, no matter what the exit
                            code of the command is.
    :param retain_output: set to True to make stdout/stderr of the command
                            output to be also sent to the logging system
    :param args: sequence of strings of arguments tp be given to the command
                inside " quotes after they have been escaped for that; each
                element in the aequence will be given as a seperate
                command argument
    :param verbose: if True, log the command being run
    :return: a string with the stdout output of the command
    """
    if retain_output:
        out = run(command, timeout=timeout, ignore_statsu=ignore_status,
                stdout_tee=TEE_TO_LOGS,
                stderr_tee=TEE_TO_LOGS, verbose=verbose, args=args).stdout
    else:
        out = run(command, timeour=timeout, ignore_status=ignore_status,
                    verbose=verbose, args=args).stdout
    if out[-1:] == '\n':
        out = out[:-1]
    return out


def system(command, timeout=None, ignore_status=False, verbose=True):
    """
    Run a command
    """
    return run(command, timeout=timeout, ignore_status=ignore_status,
            stdout_tee=TEE_TO_LOGS,
            stderr_tee=TEE_TO_LOGS, verbose=verbose).exit_status


def join_bg_jobs(bg_jobs, timeout=None):
    """
    Joins the bg_jobs with the current thread.
    Returns the same list of bg_jobs objects that was passed in.
    """
    ret, timeout_error = 0, False
    for bg_job in bg_jobs:
        bg_job.output_prepare(StringIO.StringIO(), StringIO.StringIO())

    try:
        # We are holding ends to stdin, stdout pipes
        # hence we need to be sure to close those fds no mater what
        start_time = time.time()
        timeout_error = _wait_for_commands(bg_jobs, start_time, timeout)

        for bg_job in bg_jobs:
            # Process stdout and stderr
            bg_job.process_output(stdout=True, final_read=True)
            bg_job.process_output(stdout=False, final_read=True)
    finally:
        # close our ends of the pipes to the sp no matter what
        for bg_job in bg_jobs:
            bg_job.cleanup()

    if timeout_error:
        # TODO: This needs to be fixed to better represent what happens when
        # running in parallel. However this is backwards compatible, so it will
        # do for the time being.
        raise error.CmdError(bg_jobs[0].command, bg_jobs[0].result,
                         "Command(s) did not complete within %d seconds"
                         % timeout)
    return bg_jobs


def _wait_for_commands(bg_jobs, start_time, timeout):
    # this returns True if it must return due to a timeout, otherwise False
    # to check for processes which terminate without producing any output
    # a 1 second timeout is used in select.
    SELECT_TIMEOUT = 1

    read_list = []
    write_list = []
    reverse_dict = {}

    for bg_job in bg_jobs:
        read_list.append(bg_job.sp.stdout)
        read_list.append(bg_job.sp.stderr)
        reverse_dict[bg_job.sp.stdout] = (bg_job, True)
        reverse_dict[bg_job.sp.stderr] = (bg_job, False)

        if bg_job.string_stdin is not None:
            write_list.append(bg_job.sp.stdin)
            reverse_dict[bg_job.sp.stdin] = bg_job

    if timeout:
        stop_time = start_time + timeout
        time_left = stop_time - time.time()
    else:
        time_left = None

    while not timeout or time_left > 0:
        # select will return when we may write to stdin or when there is
        # stdout/stderr output we can read (including when it is EOF, that
        # is the process har terminated).
        read_ready, write_ready, _ = select.select(read_list, write_list, [],
                                            SELECT_TIMEOUT)
        # os.read() has to be used instead of subproc.stdout.read() which
        # will otherwise block
        for file_obj in read_ready:
            bg_job, is_stdout = reverse_dict[file_obj]
            bg_job.process_output(is_stdout)

        for file_obj in write_ready:
            # we can write PIPE_BUF bytes without blocking
            # POSIX requires PIPE_BUF is >= 512
            bg_job = reverse_dict[file_obj]
            file_obj.write(bg_job.string_stdin[:512])
            bg_job.string_stdin = bg_job.string_stdin[512:]
            # no more input data, close stdin, remove it from the select set
            if not bg_job.string_stdin:
                file_obj.close()
                write_list.remove(file_obj)
                del reverse_dict[file_obj]

        all_jobs_finished = True
        for bg_job in bg_jobs:
            if bg_job.result.exit_status is not None:
                continue
            bg_job.result.exit_status = bg_job.sp.poll()

            if bg_job.result.exit_status is not None:
                # process exited, remove its stdout/stdin from the select set
                bg_job.result.duration = time.time() - start_time
                read_list.remove(bg_job.sp.stdout)
                read_list.remove(bg_job.sp.stderr)
                del reverse_dict[bg_job.sp.stdout]
                del reverse_dict[bg_job.sp.stderr]
            else:
                all_jobs_finished = False

        if all_jobs_finished:
            return False

        if timeout:
            time_left = stop_time - time.time()

    # kill all processed which did not complete prior to timeout
    for bg_job in bg_jobs:
        if bg_job.result.exit_status is not None:
            continue

        logging.warn('run process timeout (%s) fired on: %s', timeout,
                bg_job.command)
        nuke_subprocess(bg_job.sp)
        bg_job.result.exit_status = bg_job.sp.poll()
        bg_job.result.duration = time.time() - start_time
    return True


def safe_rmdir(path, timeout=10):
    """
    try to remove a directory safely, even on NFS filesystems
    """
    assert os.path.isdir(path), "Invalid directory to remove %s" % path
    step = int(timeout / 10)
    start_time = time.time()
    success = False
    attempts = 0
    while int(time.time() - start_time) < timeout:
        attempts += 1
        try:
            shutil.rmtree(path)
            success = True
            break
        except OSError, err_info:
            if err_info.errno != 39:
                raise
            time.sleep(step)
    if not success:
        raise OSError(39, "Could not delete directory %s after %d s"
                            "and %d attempts."
                            % (path, timeout, attempts))


def wait_for(func, timeout, first=0.0, step=1.0, text=None):
    """
    If func() evaluates to True before timeout expires, return the
    value of func(). Otherwise return None.

    @brief: Wait until func() evaluates to True.

    :param timeout: Timeout in seconds
    :param first: Time to sleep before first attempt
    :param steps: Time to sleep between attempts in seconds
    :param text: Text to print while waiting, for debug purposes
    """
    start_time = time.time()
    end_time = time.time() + timeout
    time.sleep(first)
    while time.time() < end_time:
        if text:
            logging.debug("%s (%f secs)", text, (time.time() - start_time))
        output = func()
        if output:
            return output
        time.sleep(step)
    return None
