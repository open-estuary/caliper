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

    """ For 'android', we need to read the 'common_cases_def.cfg' and
        'android_case_def.cfg';
        For 'arm', need to read the 'common_case_def.cfg' and
        'arm_cases_def.cfg';
        For 'x86', need to read the 'common_case_def.cfg' and
        'server_cases_def.cfg'.
    """
    def get_cases_def_files(self):
        cfg_files = []
        cases_tail = "_cases_def.cfg"
        common_cfg = "common" + cases_tail
        common_cfg_path = os.path.join(
                                caliper_path.config_files.tests_cfg_dir,
                                common_cfg)
        cfg_files.append(common_cfg_path)
        if (self.arch == 'arm_32'):
            other_cfg = "arm" + cases_tail
        elif (self.arch == 'android'):
            other_cfg = "android" + cases_tail
        elif (self.arch == 'arm_64'):
            other_cfg = "server" + cases_tail
        else:
            other_cfg = 'server' + cases_tail
        other_cfg_path = os.path.join(caliper_path.config_files.tests_cfg_dir,
                                        other_cfg)
        cfg_files.append(other_cfg_path)
        return cfg_files

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


def get_bench_info(config_file, bench_name):
    baseCfg = BaseCfg(config_file)
    try:
        build_file = baseCfg.get_value(bench_name, 'build')
        run_config = baseCfg.get_value(bench_name, 'run')
        parser_file = baseCfg.get_value(bench_name, 'parser')
        location = baseCfg.config_file.strip().split("/")[-1].split["_"][0]
    except Exception:
        logging.debug("There is error with the config file: %s" % config_file)
        raise
    else:
        location = os.path.join(caliper_path.config_files.tests_cfg_dir,
                                    location)
        build_file = get_real_files(location, build_file)
        run_config = get_real_files(location, run_config)
        parser_file = get_real_files(location, parser_file)
    return build_file, run_config, parser_file
