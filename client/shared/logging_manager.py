#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Date    :   15/01/06 08:39:35
#   Desc    :
#

import logging

logger = logging.getLogger()


def _current_handlers():
    return set(logger.handlers)


_caller_code_to_skip_in_logging_stack = set()


def do_not_report_as_logging_caller(func):
    """Decorator to annotate functions we will tell logging not to log."""
    # These are not the droids you are looking for.
    # You may go about your business.
    _caller_code_to_skip_in_logging_stack.add(func.func_code)
    return func


class LoggingFile(object):
    """
    File-like object that will receive messages pass them to the logging
    infrastructure in an appropriate way.
    """

    def __init__(self, prefix='', level=logging.DEBUG,
            logger=logging.getLogger()):
        """
        :param prefix - the prefix for each line logged by this object
        """
        self._prefix = prefix
        self._level = level
        self._buffer = []
        self._logger = logger

    @do_not_report_as_logging_caller
    def write(self, data):
        """
        Writes data only if it constitues a whileone line. If it is not the
        case, store it in a buffer and wait until we have a complete line.
        """
        data_lines = data.split('\n')
        if len(data_lines) > 1:
            self._buffer.append(data_lines[0])
            self._flush_buffer()
        for line in data_lines[1:-1]:
            self._log_line(line)
        if data_lines[-1]:
            self._buffer.append(data_lines[-1])

    @do_not_report_as_logging_caller
    def writelines(self, lines):
        """
        Writes iterable of lines
        """
        for data in lines:
            self.write(data)

    @do_not_report_as_logging_caller
    def _log_line(self, line):
        """ passes lines of output to the logging module """
        self._logger.log(self._level, self._prefix+line)

    @do_not_report_as_logging_caller
    def _flush_buffer(self):
        if self._buffer:
            self._log_line(''.join(self._buffer))
            self._buffer = []

    @do_not_report_as_logging_caller
    def flush(self):
        self._flush_buffer()

    def isatty(self):
        return False
