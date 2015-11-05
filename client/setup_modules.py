#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Date    :   15/01/07 11:06:50
#   Desc    :
#

import os
import sys

import new
import imp


def _create_module(name):
    """
    Create a single top-level module and add it to sys.modules.
    """
    module = new.module(name)
    sys.modules[name] = module
    return module


def _create_module_and_parents(name):
    """
    Create a module, and all the necessary parents and add them to sys.modules.
    :param name: Module name, such as 'autptest.client'.
    """

    parts = name.split(".")
    # frist create the top-level module
    parent = _create_module(parts[0])
    created_parts = [parts[0]]
    parts.pop(0)

    # now, create any remaining child modules
    while parts:
        child_name = parts.pop(0)
        module = new.module(child_name)
        setattr(parent, child_name, module)
        created_parts.append(child_name)
        sys.modules[".".join(created_parts)] = module
        parent = module


def import_module(module, from_where):
    """
    Equivalent to 'from from_where import module'
    :param module: Module name
    :param from_where: Package from where the module is being imported.
    :return: the corresponding module
    """
    from_module = __import__(from_where, globals(), locals(), [module])
    return getattr(from_module, module)


def setup(base_path, root_module_name="caliper"):
    """
    Setup a library namespace, with the appropriate top root module name.

    Perform all the necessary setup so that all the packages at 'base_path' can
    be imported via 'import root_module_name,package'
    :param base_path: Base path for the module
    :parma root_module_name: Top level name for the module
    """
    if sys.modules.has_key(root_module_name):
        return
    _create_module_and_parents(root_module_name)
    imp.load_package(root_module_name, base_path)

    # allow locally installed third party packages to be found.
    sys.path.insert(0, os.path.join(base_path, "site_packages"))
