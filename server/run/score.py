#!/usr/bin/env python

import os
import types
import string
import re
import logging

import yaml
try:
    import caliper.common as common
except ImportError:
    import common
from caliper.server import utils as server_utils
from caliper.server.shared import caliper_path
from caliper.server.run import write_results
from caliper.server.shared.caliper_path import folder_ope as Folder


def compute_caliper_logs(target_exec_dir, flag=1):
    # according the method in the config file, compute the score
    dic = yaml.load(open(caliper_path.folder_ope.final_parser, 'r'))
    sections, run_case_list = common.read_config()
    for j in range(0, len(sections)):
        common.print_format()
        if flag == 1:
            logging.info("Generation raw yaml for %s" % sections[j])
            bench = os.path.join(caliper_path.BENCHS_DIR, sections[j], 'defaults')
        else:
            logging.info("Computing Score for %s" % sections[j])
            bench = os.path.join(caliper_path.BENCHS_DIR, sections[j], 'defaults')
        try:
            # get the abspath, which is filename of run config for the benchmark
            bench_conf_file = os.path.join(bench, 'main.yml')
            # get the config sections for the benchmrk
            pf = open(bench_conf_file, 'r')
            values = yaml.load(pf.read())
            sections_run = values[sections[j]].keys()
        except AttributeError as e:
            raise AttributeError
        except Exception:
            raise
        for section in sections_run:
            if section in run_case_list:
                try:
                    category = values[sections[j]][section]['category']
                    scores_way = values[sections[j]][section]['scores_way']
                    command = values[sections[j]][section]['command']
                except Exception, e:
                    logging.debug("no value for the %s" % section)
                    logging.info(e)
                    continue
                try:
                    logging.debug("Computing the score of the result of command: %s"
                                  % command)
                    flag_compute = compute_case_score(dic[sections[j]][section]["value"], category,
                                                      scores_way, target_exec_dir, flag)
                except Exception, e:
                    logging.info("Error while computing the result of \"%s\"" % section)
                    logging.info(e)
                    continue
                else:
                    if not flag_compute and dic[bench][section["value"]]:
                        logging.info("Error while computing the result\
                                        of \"%s\"" % command)
            else:
                continue
    logging.info("=" * 55)
    if not os.path.exists(caliper_path.HTML_DATA_DIR_INPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_INPUT)

    if not os.path.exists(caliper_path.HTML_DATA_DIR_OUTPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_OUTPUT)

def compute_case_score(result, category, score_way, target, flag):
    tmp = category.split()
    length = len(tmp)
    # write the result and the corresponding score to files
    target_name = server_utils.get_host_name(target)
    yaml_dir = os.path.join(Folder.results_dir, 'yaml')
    result_yaml_name = target_name + '.yaml'
    score_yaml_name = target_name + '_score.yaml'
    if flag == 1:
        result_yaml = os.path.join(yaml_dir, result_yaml_name)
    else:
        result_yaml = os.path.join(yaml_dir, score_yaml_name)
    if (length == 4 and tmp[0] == 'Functional'):
        return compute_func(result, tmp, score_way, result_yaml, flag)
    elif ((length != 0 and length <= 4) and tmp[0] == 'Performance'):
        return compute_perf(result, tmp, score_way, result_yaml, flag)
    else:
        return -4


def compute_func(result, tmp, score_way, result_yaml, flag=1):
    flag1 = 0
    if flag == 2:
        result = result * 100
    try:
        flag1 = write_results.write_yaml_func(result_yaml,
                                              tmp, result,
                                              flag)
    except BaseException:
        logging.debug("There is wrong when computing the score")
    return flag1

def compute_perf(result, tmp, score_way, result_yaml, flag=1):
    result_flag = 1
    score_flag = 2

    if type(result) is types.StringType:
        if re.search('\+', result):
            result = result.replace('\+', 'e')
        result_fp = string.atof(result)
    elif type(result) is types.FloatType:
        result_fp = result
    elif type(result) is types.IntType:
        result_fp = result
    elif (type(result) == dict and (len(tmp) > 0 and len(tmp) < 4)):
        return deal_dic_for_yaml(result, tmp, score_way,
                                 result_yaml, flag)
    else:
        return -4

    if flag == 2:
        result_fp = write_results.compute_score(score_way, result_fp)
    flag1 = 0
    try:
        flag1 = write_results.write_yaml_perf(result_yaml, tmp,
                                              result_fp, flag)
    except BaseException:
        logging.debug("There is wrong when compute the score.")
    return flag1

def deal_dic_for_yaml(result, tmp, score_way, yaml_file, flag):
    if (len(tmp) == 2):
        status = write_results.write_dic(result, tmp, score_way,
                                         yaml_file, flag)
    elif (len(tmp) == 3):
        status = write_results.write_sin_dic(result, tmp, score_way, yaml_file, flag)
    else:
        status = write_results.write_multi_dic(result, tmp, score_way,
                                               yaml_file, flag)
    return status