#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import logging

try:
    import caliper.common
except ImportError:
    import common

from caliper.client.shared import error
from caliper.client.shared import utils
from caliper.client.shared.settings import settings
from caliper.server.hosts import host_factory


class RemoteBMCer(object):
    command = None
    host = ''

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(RemoteBMCer, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

    def remote_BMC_operate(self):
        returncode = -1

        try:
            self.get_BMC_host()
        except Exception as e:
            return returncode

        if not self.host or not self.command:
            return returncode

        try:
            result = self.host.run(self.command)
        except error.CmdError, e:
            raise error.ServRunError(e.args[0], e.args[1])
        except Exception as e:
            logging.info(e)
        else:
            if result.exit_status:
                returncode = result.exit_status
            else:
                returncode = 0
        return returncode

    def get_BMC_host(self):
        try:
            bmc_ip = settings.get_value('BMCER', 'host', type=str)
            port = settings.get_value('BMCER', 'port', type=int)
            user = settings.get_value('BMCER', 'user', type=str)
            passwd = settings.get_value('BMCER', 'password', type=str)
            command = settings.get_value('BMCER', 'command', type=str)
        except Exception as e:
            raise error.ServRunError(e.args[0], e.args[1])
        else:
            self.command = command
            try:
                bmc_host = host_factory.create_host(bmc_ip, user, passwd, port)
            except Exception as e:
                raise error.ServRunError(e.args[0], e.args[1])
            else:
                self.host = bmc_host


def judge_target_crash():
    result = -1
    try:
        client = settings.get_value('TARGET', 'ip', type=str)
        commands = 'ping -c 10 %s' % client
        result = utils.run(commands)
    except error.CmdError:
        return True
    else:
        if result.exit_status:
            return True
        else:
            output = result.stdout
            if re.search("100%\spacket\sloss", output):
                return True
            else:
                return False


def main():
    if judge_target_crash():
        bmcer = RemoteBMCer()
        bmcer.remote_BMC_operate()
        time.sleep(200)
