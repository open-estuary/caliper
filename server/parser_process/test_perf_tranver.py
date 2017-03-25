#!/usr/bin/env python

import os
import sys
import shutil
import yaml
import logging
import json
import string

try:
    import caliper.common
except ImportError:
    import common

from caliper.server.compute_model.scores_method import geometric_mean
import caliper.server.utils as server_utils

point_str = 'Point_Scores'
total_str = 'Total_Scores'
results_str = 'results'
perf_str = 'Performance'
func_str = 'Functional'
conf_str = 'Configuration'
name_str = 'name'


def traverse_pre(target, dic_file):
    """ dic_file means sections in the yaml file which store the information
    of machine """
    if name_str not in dic_file:
        dic_file[name_str] = {}
    hostName = server_utils.get_host_name(target)
    dic_file[name_str] = hostName
    if conf_str not in dic_file:
        dic_file[conf_str] = {}
    dic_file[conf_str] = server_utils.get_host_hardware_info(target)
    return dic_file


def traverse_score(results):
    keys_sub_items = results.keys()

    for subItem in keys_sub_items:
        test_point_dic = results[subItem]
        key_test_points = test_point_dic.keys()
        values_test_points = []

        # get the geometric value for each point
        for test_point in key_test_points:
            test_case_dic = test_point_dic[test_point]
            point_values = test_case_dic[point_str].values()
            useful_values = [string.atof(x) for x in point_values
                                if string.atof(x) != 0]
            if len(useful_values) < 1:
                last_result = 0
            else:
                try:
                    last_result = geometric_mean(useful_values)
                    last_result = round(last_result, 2)
                except TypeError, e:
                    logging.info(e)
                    continue

            test_case_dic[total_str] = last_result
            values_test_points.append(last_result)

        # get geometric value for each testItem
        if len(values_test_points) < 1:
            total_sub_items_result = 0
        else:
            try:
                total_sub_items_result = geometric_mean(values_test_points)
            except TypeError, e:
                logging.info("Compute the last score of subItem %s wrong" %
                                subItem)
                logging.info(e)
            else:
                if total_str not in test_point_dic:
                    test_point_dic[total_str] = {}
                test_point_dic[total_str] = round(total_sub_items_result, 2)
    return results


def traverser_results(target, yaml_file):
    flag = 0
    yaml_file_post = yaml_file[0:-5] + "_post" + yaml_file[-5:]
    if os.path.exists(yaml_file):
        shutil.copyfile(yaml_file, yaml_file_post)
    else:
        logging.info("No such file %s" % yaml_file)
        flag = -1
        return flag
    fp = open(yaml_file)
    dic_ = yaml.load(fp)
    fp.close()

    if perf_str in dic_[results_str].keys():
        perf_results = dic_[results_str][perf_str]
        dic_[results_str][perf_str] = traverse_score(perf_results)
    if func_str in dic_[results_str].keys():
        func_results = dic_[results_str][func_str]
        dic_[results_str][func_str] = traverse_score(func_results)

    dic_ = traverse_pre(target, dic_)

    with open(yaml_file_post, 'w') as outfile:
        outfile.write(yaml.dump(dic_, default_flow_style=False))
        flag = 1
    outfile.close()
    json_file_post = yaml_file[0:-5] + "_post.json"
    json.dump(dic_, open(json_file_post, 'w'))
    return flag

if __name__ == "__main__":
    target = sys.argv[1]
    file_name = sys.argv[2] + "/yaml/Ur_machine_score.yaml"
    result = traverser_results(target, file_name)
    if result != 1:
        logging.info("There is wrong")
