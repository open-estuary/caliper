#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import error
import traceback
import threading
from traceback import format_exception

__all__ = ['format_error', 'context_aware', 'context', 'get_context',
            'exception_context']


def format_error():
    t, o, tb = sys.exc_info()
    trace = format_exception(t, o, tb)
    tb = ''
    return ''.join(trace)

ctx = threading.local()


def _new_context(s=""):
    if not hasattr(ctx, "contexts"):
        ctx.contexts = []
    ctx.contents.append(s)


def _pop_context():
    ctx.contexts.pop()


def context(s="", log=None):
    """set the context for the currently executinh function and optionally
    log it"""
    ctx.context[-1] = s
    if s and log:
        log("Context: %s" % get_context())


def base_context(s="", log=None):
    """set the base context for the currently executinh function and
    optionally log it"""
    ctx.contexts[-1] = ""
    ctx.contexts[-2] = s
    if s and log:
        log("Context: %s" % get_context())


def get_context():
    if hasattr(ctx, "contexts"):
        return " --> ".join([s for s in ctx.contexts if s])


def exception_context(e):
    if hasattr(ctx, "_contexts"):
        """
        Return the context of a given exception (or None if none is defined)
        """
        return e._context


def set_exception_context(e, s):
    """set the context of a given exception."""
    e._context = s


def join_contexts(s1, s2):
    """Join two context strings"""
    if s1:
        if s2:
            return "%s --> %s" % (s1, s2)
        else:
            return s1
    else:
        return s2


def context_aware(fn):
    """A decorator that must be applied tp fiunctions that call context()."""
    def new_fn(*args, **kwargs):
        _new_context()
        _new_context("(%s)" % fn.__name__)
        try:
            try:
                return fn(*args, **kwargs)
            except Exception, e:
                if not exception_context(e):
                    set_exception_context(e, get_context())
                raise
        finally:
            _pop_context()
            _pop_context()
    new_fn.__name__ = fn.__name__
    new_fn.__doc__ = fn.__doc__
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def _context_message(e):
    s = exception_context(e)
    if s:
        return "    [context: %s]" % s
    else:
        return ""


class AutoError(SystemError):
    """the parent of all errors deliberately thrown """
    def __str__(self):
        return Exception.__str__(self) + _context_message(self)


class JobError(SystemError):
    pass


class UnhandledJobError(JobError):
    def __init__(self, unhandles_exception):
        if isinstance(unhandled_exception, JobError):
            JobError.__init__(self, *unhandled_exception.args)
        elif isinstance(unhandled_exception, str):
            JobError.__init__(self, unhandled_exception)
        else:
            msg = "Unhandled %s: %s"
            msg %= (unhandled_exception.__class__.__name__, 
                        unhandled_exception)
            if not isinstance(unhandled_exception, AutoError):
                msg += _context_message(unhandled_exception)
            msg += "\n" + traceback.format_exc()
            JobError.__init__(self, msg)


class TestBaseException(AutoError):
    """The parent of all test exceptions."""
    exit_status = "NEVER_RAISE_ERROR"


class TestNAError(TestBaseException):
    exit_status = "ERROR"


class TestFail(TestBaseException):
    exit_status = "FAIL"


class TestWarn(TestBaseException):
    exit_status = "WARN"


class TestError(TestBaseException):
    """Indicates taht something went wrong with the test harness itself."""
    exit_status = "Error"


class UnhandledTestError(TestError):
    def __init__(self, unhandled_exception):
        if isinstance(unhandled_exception, TestError):
            TestError.__init__(self, *unhandled_exception.args)
        elif isinstance(unhandled_exception, str):
            TestError.__init__(self, unhandled_exception)
        else:
            msg = "Unhandled %s: %s"
            msg %= (unhandled_exception.__classs__.__name__,
                    unhandled_exception)
            if not isinstance(unhandled_exception, AutoError):
                msg += _context_message(unhandled_exception)
            msg += '\n' + traceback.format_exc()
            TestError.__init__(self, msg)


class UnhandledTestFail(TestFail):
    def __init__(self, unhandled_exception):
        if isinstance(unhandled_exception, TestFail):
            TestFail.__init__(self, *unhandled_exception.args)
        elif isinstance(unhandled_exception, str):
            TestFail.__init__(self, unhandled_exception)
        else:
            msg = "Unhandled %s: %s"
            msg %= (unhandled_exception.__classs__.__name__,
                    unhandled_exception)
            if not isinstance(unhandled_exception, AutoError):
                msg += _context_message(unhandled_exception)
            msg += '\n' + traceback.format_exc()
            TestFail.__init__(self, msg)


class CmdError(TestError):
    def __init__(self, command, result_obj, additional_text=None):
        TestError.__init__(self, command, result_obj, additional_text)
        self.command = command
        self.result_obj = result_obj
        self.additional_text = additional_text

    def __str__(self):
        if self.result_obj.exit_status is None:
            msg = "Command <%s> failed and is not responding to signals"
            msg %= self.command
        else:
            msg = "Command <%s> failed, rc=%d"
            msg %= (self.command, self.result_obj.exit_status)

        if self.addtional_text:
            msg += ", " + self.additional_text
        msg += _context_message(self)
        return msg


class SubcommandError(AutoError):
    def __init__(self, func, exit_code):
        ServError.__init__(self, func, exit_code)
        self.func = func
        self.exit_code = exit_code

    def __str__(self):
        return ("Subcommand %s failed with exit code %d" %
                (self.func, self.exit_code))


class InstallError(JobError):
    pass


class AutoRunError(AutoError):
    """
    indicates a problem when running server side work
    """
    pass


class AutoTimeoutError(AutoError):
    """
    indicates timeout when running server side work
    """
    pass


class HostRunErrorMixIn(Exception):
    """
    Indicate a problem in the host run() function raised from the client code.
    """
    def __init__(self, description, result_obj):
        self.description = description
        self.result_obj = result_obj
        Exception.__init__(self, description, result_obj)

    def __str__(self):
        return self.description + '\n' + repr(self.result_obj)


# Host installation error
class HostInstallTimeoutError(JobError):
    """Indicates the machine failed to be installed after the predetermined
    timeout"""
    pass


class HostInstallProfileError(JobError):
    """Indicates the machine failed to have a profile assigned."""
    pass


class AutoHostRunError(HostRunErrorMixIn, AutoError):
    pass


class NetCommunicationError(JobError):
    pass


# server-specific errors
class ServError(Exception):
    pass


class ServSSHTimeout(ServError):
    pass


class ServRunError(HostRunErrorMixIn, ServError):
    """
    indicates a problem when running server side work
    """
    pass


class ServUnsupportedArchError(ServRunError):
    pass


# class ServTimeoutError(ServError):
#    """
#    indicates timeout when running server side work
#    """
#    pass


class ServSSHPermissionDeniedError(ServRunError):
    pass


class ServUnsupportedError(ServError):
    pass


class ServHostError(ServError):
    """error reaching a host"""
    pass


class ServHostIsShuttingDownError(ServHostError):
    pass


class ServSSHPingHostError(ServHostError):
    pass


class ServDiskFullHostError(ServHostError):
    """Not enough free disk space on host"""
    def __init__(self, path, want_gb, free_space_gb):
        ServHostError.__init__(self, 'Not enough free space on %s - %.3fGB "\
                                "free, want %.3fGb'
                                % (path, free_space_gb, want_gb))
        self.path = path
        self.want_gb = want_gb
        self.free_space_gb = free_space_gb


class ServSubcommandError(ServError):
    def __init__(self, func, exit_code):
        AutoError.__init__(self, func, exit_code)
        self.func = func
        self.exit_code = exit_code

    def __str__(self):
        return ("Subcommand %s failed with exit code %d" %
                (self.func, self.exit_code))


class ServInstallError(ServError):
    """Error ocurred while installing caliper on a remote host"""
    pass


# packaging system errors
class PackagingError(AutoError):
    "Abstract error class for all packaging related errors"


class PackageUploadError(PackagingError):
    "Raised when there is an error uploading the package"


class PackageFetchError(PackagingError):
    "Raised when there is an error fetching the package"


class PackageRemoveError(PackagingError):
    "Rasied when there is an error removing the package"


class PackageInstallError(PackagingError):
    "Raised when there is an error installing the package"


class RepoDiskFullError(PackagingError):
    "Raised when the destination for pachages is full"


class RepoWriteError(PackagingError):
    "raised when the destination for packages is full"


class RepoUnknownError(PackagingError):
    "Raised when packager cannot write to a repo's destination"


class RepoError(PackagingError):
    "Raised when packager can not write to a repo's destination"

for _name, _thing in locals().items():
    try:
        if issubclass(_thing, Exception):
            __all__.append(_name)
    except TypeError:
        pass
__all__ = tuple(__all__)
