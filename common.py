#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

try:
    import caliper.client.setup_modules as setup_modules
    dirname = os.path.dirname(setup_modules.__file__)
    caliper_dir = os.path.join(dirname, "..")
except ImportError:
    dirname = os.path.dirname(sys.modules[__name__].__file__)
    caliper_dir = os.path.abspath(dirname)
    client_dir = os.path.join(caliper_dir, "client")
    sys.path.insert(0, client_dir)
    import setup_modules
    sys.path.pop(0)

setup_modules.setup(base_path=caliper_dir, root_module_name="caliper")

import caliper.server
