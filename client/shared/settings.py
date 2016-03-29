#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Date    :   15/01/07 19:21:42
#   Desc    :
#

import os
import ConfigParser
from caliper.client.shared import error
from caliper.client.shared import caliper_path


class SettingsError(error.AutoError):
    pass


class SettingsValueError(SettingsError):
    pass

settings_filename = 'client_config.cfg'
shadow_config_filename = 'shadow_config.cfg'

settings_path_root = os.path.join(
                        caliper_path.config_files.config_dir,
                        settings_filename)
config_in_root = os.path.exists(settings_path_root)

# need to change
if config_in_root:
    DEFAULT_CONFIG_FILE = settings_path_root
    RUNNING_STAND_ALONE_CLIENT = False
else:
    DEFAULT_CONFIG_FILE = None
    RUNNING_STAND_ALONE_CLIENT = False

class Settings(object):
    _NO_DEFAULT_SPECIFIED = object()

    config = None
    config_file = DEFAULT_CONFIG_FILE
    running_stand_alone_client = RUNNING_STAND_ALONE_CLIENT

    def check_stand_alone_client_run(self):
        return self.running_stand_alone_client

    def set_config_files(self, config_file=DEFAULT_CONFIG_FILE):
        self.config_file = config_file
        self.config = self.parse_config_file()

    def _handle_no_value(self, section, key, default):
        if default is self._NO_DEFAULT_SPECIFIED:
            msg = ("Value '%s' not found in section '%s'" % (key, section))
            raise SettingsError(msg)
        else:
            return default

    def get_section_values(self, sections):
        """
        Return a config parser object containing a single section of the
        global configuration, that can be written to a file object.

        :param
        section: Tuple with sections we want to turn into a config
                        parser
        :return: ConfigParser() onject containing all the contents of
                        sections.
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

    def get_value(self, section, key, type=str, default=_NO_DEFAULT_SPECIFIED,
                    allow_blank=False):
        self._ensure_config_parsed()

        try:
            val = self.config.get(section, key)
        except ConfigParser.Error:
            return self._handle_no_value(section, key, default)

        if not val.strip() and not allow_blank:
            return self._handle_no_values(section, key, default)

        return self._convert_value(key, section, val, type)

    def override_value(self, section, key, new_value):
        """
        Override a value from the config file with a new value.
        """
        self._ensure_config_parsed()
        self.config.set(section, key, new_value)

    def reset_values(self):
        """
        Reset all values to those found in the config files (undoes all
        overrides).
        """
        self.parse_config_file()

    def _ensure_config_parsed(self):
        if self.config is None:
            self.parse_config_file()

    def merge_configs(self, shadow_config):
        # overwrite whats in config with whats in shadow_config
        sections = shadow_config.sections()
        for section in sections:
            # add the section if needed
            if not self.config.has_section(section):
                self.config.add_section(section)

            # now run through all options and set them
            options = shadow_config.options(section)
            for option in options:
                val = shadow_config.get(section, option)
                self.config.set(section, option, val)

    def parse_config_file(self):
        self.config = ConfigParser.ConfigParser()
        if self.config_file and os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise SettingsError('%s not found' % (self.config_file))

    # the values pulled from ini are strings
    # try to convert them to other types if needed.
    def _convert_value(self, key, section, value, value_type):
        sval = value.strip()

        if len(sval) == 0:
            if value_type == str:
                return
            elif value_type == bool:
                return False
            elif value_type == int:
                return 0
            elif value_type == float:
                return 0.0
            elif value_type == list:
                return []
            else:
                return None

        if value_type == bool:
            if sval.lower() == "false":
                return False
            else:
                return True

        if value_type == list:
            return [val.strip() for val in sval.split('.')]

        try:
            conv_val = value_type(sval)
            return conv_val
        except Exception:
            msg = ("Could not convert %s value in section %s to type %s" %
                    (key, sval, section, value_type))
            raise SettingsValueError(msg)

# insure the class is a singleton. Now the symbol settings will point to the
# one and only one instance pof the class
settings = Settings()
