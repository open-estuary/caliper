## wuyanjun 00291783
## wu.wu@hisilicon.com
## Copyright

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

def traverse_pre(target, dic_file):
    """ dic_file means sections in the yaml file which store the information of machine """
    if 'name' not in dic_file:
        dic_file['name'] = {}
    hostName = server_utils.get_host_name( target )
    dic_file['name'] = hostName

    if 'Configuration' not in dic_file:
        dic_file['Configuration'] = {}

    dic_file['Configuration'] = server_utils.get_host_hardware_info(target)

    return dic_file

def traverser_perf(target, yaml_file):
    flag = 0
    yaml_file_post = yaml_file[0:-5] + "_post" + yaml_file[-5:]
    if os.path.exists(yaml_file):
        shutil.copyfile(yaml_file, yaml_file_post)
    else:
        logging.info( "No such file %s" % yaml_file )
        flag = -1
        return flag
    fp = open(yaml_file)
    dic_perf = yaml.load(fp)
    fp.close()
    perf_results = dic_perf['results']['Performance']
    keys_sub_items = perf_results.keys()

    for subItem in keys_sub_items:
        test_point_dic = perf_results[subItem]
        key_test_points = test_point_dic.keys()
        values_test_points = []

        for test_point in key_test_points:
            test_case_dic = test_point_dic[test_point]
            point_values = test_case_dic['Point_Scores'].values()
            useful_values = [string.atof(x) for x in point_values if string.atof(x) != 0 ]
            if len(useful_values) < 1:
                last_result = 0
            else:
                try:
                    last_result = geometric_mean(useful_values)
                    last_result = round(last_result, 2)
                except TypeError, e:
                    logging.info( e )
                    continue

            test_case_dic['Total_Scores'] = last_result
            values_test_points.append(last_result)

        if len(values_test_points) < 1:
            total_sub_items_result = 0
        else:
            try:
                total_sub_items_result = geometric_mean(values_test_points)
            except TypeError, e:
                logging.info( "Compute the last score of subItem %s wrong" % subItem )
                logging.info(e)
            else:
                if 'Total_Scores' not in test_point_dic:
                    test_point_dic['Total_Scores'] = {}
                test_point_dic['Total_Scores'] = round(total_sub_items_result, 2)

    dic_perf['results']['Performance'] = perf_results
    #logging.info(dic_perf)

    dic_perf = traverse_pre(target, dic_perf)
   
    with open(yaml_file_post, 'w') as outfile:
        outfile.write(yaml.dump(dic_perf, default_flow_style=False))
        flag = 1
    outfile.close()
    json_file_post = yaml_file[0:-5] + "_post.json"
    json.dump(dic_perf, open(json_file_post, 'w'))
    return flag

if __name__=="__main__":
    target = sys.argv[1]
    file_name = sys.argv[2] + "/yaml/Ur_machine_score.yaml"
    result = traverser_perf(target, file_name)
    if result != 1:
        logging.info("There is wrong")

