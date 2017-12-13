import os
import sys
import logging
import yaml
from caliper.server.shared import caliper_path
try:
    import caliper.client.setup_modules as setup_modules
    client_dir = os.path.dirname(setup_modules.__file__)
except ImportError:
    dirname = os.path.dirname(sys.modules[__name__].__file__)
    caliper_dir = os.path.abspath(os.path.join(dirname, "..", ".."))
    client_dir = os.path.join(caliper_dir, "client")
    sys.path.insert(0, client_dir)
    import setup_modules
    sys.path.pop(0)

setup_modules.setup(base_path=client_dir,
                    root_module_name="caliper.client")


def print_format():
    logging.info("=" * 55)

def read_config():
    config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
    fp = open(config_files, 'r')
    tool_list = []
    run_case_list = []
    case_list = yaml.load(fp.read())
    for dimension in case_list:
        for i in range(len(case_list[dimension])):
            for tool in case_list[dimension][i]:
                for case in case_list[dimension][i][tool]:
                    if case_list[dimension][i][tool][case][0] == 'enable':
                        tool_list.append(tool)
                        run_case_list.append(case)
    sections = list(set(tool_list))
    return sections, run_case_list