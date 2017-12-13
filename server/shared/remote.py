#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Date    :   14/12/31 15:35:58
#   Desc    :
#

import aexpect
import logging
import utils


class LoginError(Exception):
    def __init__(self, msg, output):
        Exception.__init__(self, msg, output)
        self.msg = msg
        self.output = output

    def __str__(self):
        return "%s  (output: %r)" % (self.msg, self.output)


class LoginAuthenticationError(LoginError):
    pass


class LoginTimeoutError(LoginError):
    def __init__(self, output):
        LoginError.__init__(self, "Login timeout expired", output)


class LoginProcessTerminatedError(LoginError):
    def __init__(self, status, output):
        LoginError.__init__(self, None, output)
        self.status = status

    def __str__(self):
        return ("Client process terminated   (status: %s,   output:%r)" %
                    (self.status, self.output))


class LoginBadClientError(LoginError):
    def __init__(self, client):
        LoginError.__init__(self, client)
        self.client = client

    def __str__(self):
        return "Unknown remote shell client: %r" % self.client


class SCPError(Exception):
    def __init__(self, msg, output):
        Exception.__init__(self, msg, output)
        self.msg = msg
        self.output = output

    def __str__(self):
        return "%s   (output: %r)" % (self.msg, self.output)


def handle_prompts(session, username, password, prompt, timeout=50,
                    debug=False):
    """
    Connect to a remote host (guest) using SSH or Telnet or other else.
    Wait for questions and provide answers. If timeout expires while
    waiting for output from the child  -- fail.

    :param session: An Expect or ShellSession instance to operate on
    :param username and password: to send in reply to a login
    :paramprompt: The shell prompt that indicates a successful login

    :raise LoginTimeoutError
    :rasie LoginAuthenticationError
    :raise LoginProcessTerminatedError
    :raise LoginError: If some other error occurs
    """
    password_prompt_count = 0
    login_prompt_count = 0

    while True:
        try:
            match, text = session.read_until_last_line_matches(
                        [r"[Aa]re you sure", r"[Pp]assword:\s*",
                        r"(?<![Ll]ast).*[Ll]ogin:\s*$",
                        r"[Cc]onnection.*closed", r"[Cc]onnection.*refused",
                        r"[Pp]lease wait",
                        r"[Ww]arning", r"[Ee]nter.*username",
                        r"[Ee]nter.*password", prompt
                        ],
                    timeout=timeout, internal_timeout=0.5)
            if match == 0:    # are you sure you want to continue connecting
                if debug:
                    logging.debug("Got 'Are you sure...', sending 'yes'")
                session.sendline("yes")
                continue
            elif match == 1 or match == 8:   # "password"
                if password_prompt_count == 0:
                    if debug:
                        logging.debug("Got password prompt, sending '%s'",
                                        password)
                        session.sendline(password)
                        password_prompt_count += 1
                        continue
                else:
                    raise LoginAuthenticationError(
                            "Got password prompt twice", text)
            elif match == 2 or match == 7:   # "login:"
                if login_prompt_count == 0 and password_prompt_count == 0:
                    if debug:
                        logging.debug("Got username prompt; sending '%s'",
                                        username)
                    session.sendline(username)
                    login_prompt_count += 1
                    continue
                else:
                    if login_prompt_count > 0:
                        msg = "Got username prompt twice"
                    else:
                        msg = "Got username prompt after password prompt"
                    raise LoginAuthenticationError(msg, text)
            elif match == 3:   # "Connection closed"
                raise LoginError("client said 'connection closed'", text)
            elif match == 4:   # "Connection refused"
                raise LoginError("client said 'connection refused'", text)
            elif match == 5:   # "Please wait"
                if debug:
                    logging.debug("Got 'Please wait'")
                timeout = 30
                continue
            elif match == 6:   # "warning added Rsa"
                if debug:
                    logging.debug("Got 'warning added RSA to known host list'")
                continue
            elif match == 9:   # prompt
                if debug:
                    logging.debug("Got shell prompt -- logged in")
                break
        except aexpect.ExpectTimeoutError, e:
            raise LoginTimeoutError(e.output)
        except aexpect.ExpectProcessTerminatedError, e:
            raise LoginProcessTerminatedError(e.status, e.output)


def remote_login(client, host, port, username, password, prompt, linesep="\n",
                    log_filename=None, timeout=10, interface=None):
    """
    log into a remote host(guest) using SSH/Telnet/Netcat.
    :param client       : the client to use ('ssh', 'telnet' or the other nc)
    :param host         : Hostname or IP address
    :param username     : Username (if required)
    :param password     : Password (if required)
    :param prompt       : shell prompt (regular expression)
    :param linesep      : The line separator to use when sending lines (e.g.
                            '\\n' or '\\r\\n')
    :param log_filename : if specified, log all output to this file
    :param timeout      : the maximal time duration (in seconds) to wait for
                          each step of the login procedure
    :interface          : The interface the neighbours attach to (only use
                            when using the ipv6 linklocal address.)
    :raise LoginError   : If using ipv6 linklocal but not assign a interface
                            that the neighbour attache
    :raise LoginBadClientError: If an unknown client is requested
    :raise Whatever handle_prompts() raises
    :return             : A ShellSession object
    """

    if host and host.lower().startswith("fe800"):
        if not interface:
            raise LoginError("When using ipv6 linklocal an interface must be"
                                " assigned")
        host = "%s%%%s" % (host, interface)

    if client == "ssh":
        cmd = ("ssh -o UserKnownHostsFile=/dev/null -o"
               " PreferredAuthentications=password -p %s %s@%s "
                % (port, username, host))
    elif client == "telnet":
        cmd = "telent -l %s %s %s" % (username, host, port)
    else:
        raise LoginBadClientError(client)

    logging.debug("Login Command: '%s'", cmd)
    # need to realize the aexpect.ShellSession
    session = aexpect.ShellSession(cmd, linesep=linesep, prompt=prompt)
    try:
        handle_prompts(session, username, password, prompt, timeout, True)
    except Exception:
        session.close()
        raise
    if log_filename:
        session.set_output_func(utils.log_line)
        session.set_output_params((log_filename,))
        session.set_log_file(log_filename)
    return session
