#!/usr/bin/python

import os
import sys
import logging
import re
import shutil
import glob
import yaml

import test_perf_tranver as traverse
import caliper.server.utils as server_utils
from caliper.client.shared import caliper_path

LOCATION = os.path.dirname(sys.modules[__name__].__file__)


def get_targets_data(outdir):
    yaml_dir = os.path.join(outdir, 'yaml')
    yaml_files = []
    json_files = []
    for root, dirs, files in os.walk(yaml_dir):
        for i in range(0, len(files)):
            if re.search('_score_post\.yaml', files[i]):
                yaml_name = os.path.join(root, files[i])
                yaml_files.append(yaml_name)
            else:
                if re.search('.json', files[i]):
                    json_name = os.path.join(root, files[i])
                    json_files.append(json_name)
    return (yaml_files, json_files)


def traverse_caliper_output(hosts):
    YAML_DIR = os.path.join(caliper_path.folder_ope.results_dir, 'yaml')
    host_name = server_utils.get_host_name(hosts)
    host_yaml_name = host_name + '_score.yaml'
    host_yaml_file = os.path.join(YAML_DIR, host_yaml_name)
    try:
        return_code = traverse.traverser_results(hosts, host_yaml_file)
    except Exception, e:
        logging.info(e)
        raise
    else:
        if return_code != 1:
            logging.info("there is wrong when dealing the yaml file")

def parser_caliper(host):
    try:
        traverse_caliper_output(host)
    except Exception, e:
        logging.info(e.args[0], e.args[1])
        return

    file_lists = []
    (file_lists, json_files) = get_targets_data(
                                caliper_path.folder_ope.results_dir)

    if not os.path.exists(caliper_path.HTML_DATA_DIR_INPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_INPUT)

    if not os.path.exists(caliper_path.HTML_DATA_DIR_OUTPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_OUTPUT)

    if file_lists:
        for yaml_file in file_lists:
            shutil.copy(yaml_file, caliper_path.HTML_DATA_DIR_INPUT)

    if json_files:
        for json_file in json_files:
            shutil.copy(json_file, caliper_path.HTML_DATA_DIR_INPUT)


def copy_file(host):
    '''
    copy result yaml file to caliper_output/frontend/frontend/data_files/Input_Logs
    :param host: target machine 
    :return: None
    '''
    YAML_DIR = os.path.join(caliper_path.folder_ope.results_dir, 'yaml')
    host_name = server_utils.get_host_name(host)
    host_yaml_name = host_name + '.yaml'
    hw_yaml_name = host_name + '_hw_info.yaml'
    score_yaml_name = host_name + '_score.yaml'
    host_yaml_file = os.path.join(YAML_DIR, host_yaml_name)
    hw_yaml_file = os.path.join(YAML_DIR, hw_yaml_name)
    score_yaml_file = os.path.join(YAML_DIR, score_yaml_name)
    if os.path.exists(hw_yaml_file):
        shutil.copy(hw_yaml_file, caliper_path.HW_DATA_DIR_INPUT)
    if os.path.exists(score_yaml_file):
        shutil.copy(score_yaml_file, caliper_path.HTML_DATA_DIR_INPUT)
    if os.path.exists(host_yaml_file):
        shutil.copy(host_yaml_file, caliper_path.CONSOLIDATED_DATA_DIR_INPUT)

