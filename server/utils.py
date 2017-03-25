#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import re

from caliper.client.shared.utils import *
from caliper.client.shared import error
from caliper.client.shared import caliper_path
from caliper.client.shared.settings import settings

def get_target_exec_dir(target):
    try:
        target_arch = get_host_arch(target)
    except error.ServUnsupportedError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    except error.ServRunError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    target_execution_dir = os.path.abspath(
            os.path.join(caliper_path.GEN_DIR, target_arch))
    return target_execution_dir

def get_host_arch(host):
    try:
        arch_result = host.run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])

    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            if re.search('x86_64', output):
                return 'x86_64'
            elif re.search('i[36]86', output):
                return 'x86_32'
            elif re.search('aarch64', output):
                return 'arm_64'
            else:
                if re.search('arm_32', output) or re.search('armv7', output):
                    return 'arm_32'
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)


def get_host_name(host):
    try:
        arch_result = host.run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            try:
                machine_name = settings.get_value('TARGET', 'Platform_name', type=str)
            except:
                machine_name = output.split(" ")[1]
            return machine_name
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)


def get_host_hardware_info(host):
    hardware_info = {}
    try:
        cpu_type = host.run("grep 'model name' /proc/cpuinfo |uniq \
                            |awk -F : '{print $2}' |sed 's/^[ \t]*//g'\
                            |sed 's/ \+/ /g'")
        logic_cpu = host.run("grep 'processor' /proc/cpuinfo |sort |uniq \
                            |wc -l")
        memory = host.run("free -m |grep 'Mem:' |awk -F : '{print $2}' \
                            |awk '{print $1}'")
        os_version = host.run("uname -s -r -m")

        # SPV - Fetch Cache configuration details
        l1d_cache = host.run("lscpu |grep 'L1d cache' |awk -F : '{print $2}' \
                            |awk '{print $1}'")
        l1i_cache = host.run("lscpu |grep 'L1i cache' |awk -F : '{print $2}' \
                            |awk '{print $1}'")
        l2_cache = host.run("lscpu |grep 'L2 cache' |awk -F : '{print $2}' \
                            |awk '{print $1}'")
        l3_cache = host.run("lscpu |grep 'L3 cache' |awk -F : '{print $2}' \
                            |awk '{print $1}'")
        byte_order = host.run("lscpu |grep 'Byte Order'|awk -F : '{print $2}'\
                            |awk '{print $1,$2}'")
        # More options can be added as per the requirement
        # Currently lscpu is not providing the cache related information on ARM
        # platform. A bug has been logged.
    except error.CmdError, e:
        logging.info(e.args[0], e.args[1])
        return None
    else:
        hardware_info['hostname'] = get_host_name(host)
        hardware_info['machine arch'] = get_host_arch(host)
        if not cpu_type.exit_status:
            hardware_info['CPU type'] = cpu_type.stdout.split("\n")[0]
        if not logic_cpu.exit_status:
            hardware_info['CPU'] = logic_cpu.stdout.split("\n")[0]
        if not memory.exit_status:
            hardware_info['Memory'] = memory.stdout.split("\n")[0]+'MB'
        if not os_version.exit_status:
            hardware_info['OS Version'] = os_version.stdout.split("\n")[0]

        if not l1d_cache.exit_status:
            hardware_info['l1d_cache'] = l1d_cache.stdout.split("\n")[0]
        if not l1i_cache.exit_status:
            hardware_info['l1i_cache'] = l1i_cache.stdout.split("\n")[0]
        if not l2_cache.exit_status:
            hardware_info['l2_cache'] = l2_cache.stdout.split("\n")[0]
        if not l2_cache.exit_status:
            hardware_info['l3_cache'] = l3_cache.stdout.split("\n")[0]
        if not byte_order.exit_status:
            hardware_info['byte_order'] = byte_order.stdout.split("\n")[0]
        return hardware_info


def get_local_machine_arch():
    try:
        arch_result = run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            if re.search('x86_64', output):
                return 'x86_64'
            elif re.search('i[36]86', output):
                return 'x86_32'
            elif re.search('aarch64', output):
                return 'arm_64'
            else:
                if re.search('arm_32', output) or re.search('armv7', output):
                    return 'arm_32'
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)


def get_target_ip(target):
    try:
        client_ip = settings.get_value('TARGET', 'ip', type=str)
    except Exception:
        raise
    else:
        return client_ip


def sh_escape(command):
    """
    Escape special characters from a command so that it can be passed
    as a double quoted (" ") string in a (ba)sh command
    """
    command = command.replace("\\", "\\\\")
    command = command.replace("$", r'\$')
    command = command.replace('"', r'\"')
    command = command.replace('`', r'\`')
    return command


def get_server_dir():
    path = os.path.dirname(sys.modules['caliper.server.utils'].__file__)
    return os.path.abspath(path)


def scp_remote_escape(filename):
    """
    Escape special characters from a filename so that it can be passed
    to scp (within double quotes) as a remote file.

    Bis-quoting has to be used with scp for remote files, "bis-quoting"
    as in quoting x 2
    scp does not support a newline in the filename

    Args:
        filename: the filename string to escape.

    Returns:
        The escaped filename string. The required englobing double
        quotes are NOT added and so should be added at some point by
        the caller.
    """
    escape_chars = r' !"$&' "'" r'()*,:;<=>?[\]^`{|}'

    new_name = []
    for char in filename:
        if char in escape_chars:
            new_name.append("\\%s" % (char,))
        else:
            new_name.append(char)

    return sh_escape("".join(new_name))


def parse_machine(machine, user='root', password='', port=22, profile=''):
    """
    Parser the machine string user:password@host:port and return it separately
    """
    if '@' in machine:
        user, machine = machine.split('@', 1)
    if ':' in user:
        user, password = user.split(':', 1)
    if ':' in machine:
        machine, port = machine.split(':', 1)
        try:
            port = int(port)
        except ValueError:
            port, profile = machine.split('#', 1)
            port = int(port)
    if '#' in machine:
        machine, profile = machine.split('#', 1)
    if not machine or not user:
        return ValueError
    return machine, user, password, port, profile
