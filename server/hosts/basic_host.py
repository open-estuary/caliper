#!/usr/bin/env python
# -*- coding:utf-8 -*-

# need to specify the location
from caliper.client.shared import hosts
from caliper.server import utils

class Host(hosts.Host):
    """
    this class represents the machine on which you can run programs.
    it can be a local machine, a remote machine or a virtual machine.
    this is a abstract class , leaf subclasses must implement the methods
    listed below
    """

    def __init__(self, *args, **dargs):
        super(Host, self).__init__(*args, **dargs)

        self.start_loggers()
        if self.job:
            self.job.hosts.add(self)

    def _initialize(self, target_file_owner=None, *args, **dargs):
        super(Host, self)._initialize(*args, **dargs)
        self.serverdir = utils.get_server_dir()
        self.env = {}
        self.target_file_owner = target_file_owner

    def close(self):
        super(Host, self).close()
        if self.job:
            self.job.hosts.discard(self)
