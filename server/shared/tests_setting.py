#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ConfigParser
import logging

from caliper.client.shared import error
import caliper_path

class ConfigError(error.AutoError):
    pass

# class ConfigValueError(ConfigError):
#    pass

class CfgsSelector(object):

    def __int__(self, arch):
        self.arch = arch

class BaseCfg(object):
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = None

    def get_sections(self):
        self._ensure_config_parsed()
        try:
            sections = self.config.sections()
        except Exception:
            raise
        else:
            return sections

    def get_section_values(self, sections):
        """
        return a connfig parser object containing a single section,
        that can be written to a file object
        """
        self._ensure_config_parsed()

        if isinstance(sections, str):
            sections = [sections]
        cfgparser = ConfigParser.ConfigParser()
        for section in sections:
            cfgparser.add_section(section)
            for option, value in self.config.items(section):
                cfgparser.set(section, option, value)
        return cfgparser

    def get_value(self, section, key):
        self._ensure_config_parsed()
        try:
            val = self.config.get(section, key)
        except ConfigParser.Error:
            raise ConfigError("Value '%s' not found in section '%s'" %
                                (key, section))
        else:
            return val

    def override_value(self, section, key, new_value):
        self._ensure_config_parsed()
        self.config.set(section, key, new_value)

    def _ensure_config_parsed(self):
        if self.config is None:
            self.parse_config_file()

    def parse_config_file(self):
        self.config = ConfigParser.ConfigParser()
        if self.config_file and os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise ConfigError('%s not found' % (self.config_file))


def get_real_files(location, filename):
    last_name = os.path.join(location, filename)
    if not os.path.exists(last_name):
        return ''
    else:
        return last_name

