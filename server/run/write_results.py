#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
import json
import logging
import string
import types
import glob
import copy
import sys
import shutil
import re

try:
    import caliper.common as common
except Exception:
    import common

from caliper.server.compute_model import scores_method
from caliper.server.compute_model.scores_method import Scores_method
from caliper.server.compute_model.scores_method import geometric_mean
from caliper.client.shared import caliper_path


def compute_score(score_way, result_fp):
    # this part should be improved
    func_args = score_way.split()
    score_method = func_args[0]
    if len(func_args) < 2:
        logging.info("The configuration of run the benchmark is wrong")
        return -5
    result_score = 0
    base = string.atof(func_args[1])
    if len(func_args) >= 3:
        index = string.atof(func_args[2])
    if score_method == "exp_score_compute":
        if result_fp == 0:
            result_score = 0
        else:
            try:
                result_score = Scores_method.exp_score_compute(result_fp,
                                                                base, index)
                logging.debug("After computing, the result is %f" %
                                result_score)
            except Exception, e:
                raise e
    else:
        if score_method == "compute_speed_score":
            if result_fp == 0:
                result_score = 0
            else:
                try:
                    result_score = Scores_method.compute_speed_score(
                                                            result_fp,
                                                            base)
                except Exception, e:
                    raise e
    return result_score



def write_yaml_func(yaml_file, tmp, result, kind):
    return write_yaml_perf(yaml_file, tmp, result, kind)

def write_dic(result, tmp, score_way, yaml_file, file_flag):
    flag = 0
    for key in result.keys():
        if type(result[key]) == dict:
            sub_dic = result[key]
            tmp.append(key)
            flag = write_sin_dic(sub_dic, tmp, score_way, yaml_file, file_flag)
            tmp.remove(key)
        else:
            logging.debug("There is wrong with the parser")
            flag = -1
            return flag
    flag = 1
    return flag


def write_sin_dic(result, tmp, score_way, yaml_file, file_flag):
    flag = 0
    for key in result.keys():
        if type(result[key]) == list:
            sublist = result[key]
            geo_mean = scores_method.geometric_mean(sublist)
        elif type(result[key]) is types.StringType:
            geo_mean = string.atof(result[key])
        elif type(result[key]) is types.FloatType:
            geo_mean = result[key]
        elif type(result[key]) is types.IntType:
            geo_mean = result[key]
        else:
            return -4
        tmp.append(key)

        if file_flag == 2:
            geo_mean = compute_score(score_way, geo_mean)

        flag1 = write_yaml_perf(yaml_file, tmp, geo_mean, file_flag)

        tmp.remove(key)
        if not flag1:
            return flag1
    flag = 1
    return flag


def write_multi_dic(result, tmp, score_way, yaml_file, flag_file):
    flag = 0
    for key in result.keys():
        if type(result[key]) == dict:
            try:
                sub_dic = result[key]
                tmp.append(key)
                flag = write_dic(sub_dic, tmp, score_way, yaml_file, flag_file)
                tmp.remove(key)
            except Exception:
                flag = -1
        else:
            logging.info("There is wrong with the parser")
            flag = -1
        if flag != 1:
            return flag
    flag = 1
    return flag

def round_perf(score):
    if (score < 0.1):
        score = round(score, 3)
    elif (score < 10):
        score = round(score, 2)
    else:
        score = round(score, 1)
    return score


def write_yaml_perf(yaml_file, tmp, result, kind=1):
    flag = 0
    try:
        if not os.path.exists(yaml_file):
            os.mknod(yaml_file)
            if yaml_file.endswith("_score.yaml"):
                file_name = yaml_file.split('/')[-1]
                file_name = file_name.split("_score")[0] + ".yaml"
                abs_path = yaml_file.split('/')
                abs_path[-1] = file_name
                file_name = "/".join(abs_path)
                with open(yaml_file,'w') as fp:
                    tp = open(file_name)
                    dic = yaml.load(tp)
                    dic_new = {}
                    dic_new['Configuration'] = {}
                    dic_new['Configuration'] = dic['Configuration']
                    dic_new['name'] = {}
                    dic_new['name'] = dic['name']
                    fp.write(yaml.dump(dic_new,default_flow_style=False))
    except:
        pass
    fp = open(yaml_file)
    result = round_perf(result)
    x = yaml.load(fp)
    try:
        RES = 'results'
        if not x:
            x = {}
        if RES not in x:
            x[RES] = {}
        if not x[RES]:
            x[RES] = {}
        if tmp[0] not in x[RES]:
            x[RES][tmp[0]] = {}
        if tmp[1] not in x[RES][tmp[0]]:
            x[RES][tmp[0]][tmp[1]] = {}
        if tmp[2] not in x[RES][tmp[0]][tmp[1]]:
            x[RES][tmp[0]][tmp[1]][tmp[2]] = {}
        if kind == 1:
            if tmp[3] not in x[RES][tmp[0]][tmp[1]][tmp[2]]:
                x[RES][tmp[0]][tmp[1]][tmp[2]][tmp[3]] = {}
            x[RES][tmp[0]][tmp[1]][tmp[2]][tmp[3]] = result
            flag = 1
        else:
            if kind == 2:
                if 'Point_Scores' not in x[RES][tmp[0]][tmp[1]][tmp[2]]:
                    x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'] = {}
                if not x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores']:
                    x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'] = {}
                if tmp[3] not in \
                    x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores']:
                    x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'][tmp[3]] =\
                                                                        result
                    flag = 1
                x[RES][tmp[0]][tmp[1]][tmp[2]]['Point_Scores'][tmp[3]] = result
                flag = 1
    except BaseException, e:
        logging.debug("There is wrong when write the data in file %s." % yaml)
        logging.debug(e)
        flag = -1
    else:
        fp.close()
        with open(yaml_file, 'w') as outfile:
            outfile.write(yaml.dump(x, default_flow_style=False))
        outfile.close()
        flag = 1
    return flag

def yaml_filter(yamlPath):
    scoreFile = {}
    for files in glob.glob(os.path.join(yamlPath,"*_score.yaml")):
        dic = {}
        dic = yaml.load(open(files))
        scoreFile[str(files)] = dic
    scoreFile_dic = scoreFile.values()
    logging.info("%s files are being processed for generating the reports" %len(scoreFile_dic))
    dic_ideal = ideal_dic(scoreFile_dic)
    delete_dic(dic_ideal, scoreFile_dic)
    index = 0
    for key, value in scoreFile.iteritems():
        with open(key,'w') as fp:
            fp.write(yaml.dump(scoreFile_dic[index],default_flow_style=False))
        index += 1
    return

def ideal_dic(scoreFile_dic):
    # adding exception block to handile the exception during the web report generation
    #  when any one of Functional or Performance is missing in .yaml files
    try:
        dic_ideal = copy.deepcopy(scoreFile_dic[0])
    except Exception as e:
        logging.info(e)
        sys.exit()

    for i in range(1,len(scoreFile_dic)):
        try:
            func_dic = (scoreFile_dic[i])['results']['Functional']
            populate_dic(dic_ideal['results']['Functional'], func_dic)
        except Exception as e:
            pass
        try:
            perf_dic = (scoreFile_dic[i])['results']['Performance']
            populate_dic(dic_ideal['results']['Performance'], perf_dic)
        except Exception as e:
            pass
    return dic_ideal

def populate_dic(dic_ideal, sub_dic):
    # adding exception block to handile the exception during the web report generation
    #  when any one of Functional or Performance is missing in .yaml files
    try:
        populate_dic_values(dic_ideal, sub_dic)
        populate_dic_values(dic_ideal, sub_dic, 1)
    except Exception as e:
        pass
    return

def populate_dic_values(dic_ideal, sub_dic, reverse=0):
    try:
        if reverse == 1:
            subsystem_ideal = sub_dic.keys()
            subsystem_practical = dic_ideal.keys()
        else:
            subsystem_practical = sub_dic.keys()
            subsystem_ideal = dic_ideal.keys()
        for i in subsystem_practical:
            try:
                if i in subsystem_ideal:
                    if reverse == 1:
                        scenario_ideal = sub_dic[i].keys()
                        scenario_practical = dic_ideal[i].keys()
                    else:
                        scenario_practical = sub_dic[i].keys()
                        scenario_ideal = dic_ideal[i].keys()
                    for j in scenario_practical:
                        try:
                            if j in scenario_ideal:
                                if 'Point_Scores' in dic_ideal[i][j].keys():
                                    if reverse == 1:
                                        testcases_ideal = sub_dic[i][j]['Point_Scores'].keys()
                                        testcases_pract = dic_ideal[i][j]['Point_Scores'].keys()
                                    else:
                                        testcases_pract = sub_dic[i][j]['Point_Scores'].keys()
                                        testcases_ideal = dic_ideal[i][j]['Point_Scores'].keys()
                                    for k in testcases_pract:
                                        if k not in testcases_ideal:
                                            dic_ideal[i][j]['Point_Scores'][k] = 'INVALID'
                                else:
                                    dic_ideal[i][j]['Point_Scores'] = 'INVALID'
                            else:
                                dic_ideal[i][j] = 'INVALID'
                        except:
                            pass
                else:
                    dic_ideal[i] = 'INVALID'
            except:
                pass
    except:
        pass
    return

def delete_dic(dic_ideal, scoreFile_dic):
    # adding exception block to handile the exception during the html report generation
    #  when any one of Functional or Performance is missing in .yaml files
    for i in range(len(scoreFile_dic)):
        try:
            delete_dic_values(dic_ideal['results']['Functional'], (scoreFile_dic[i])['results']['Functional'])
            if (scoreFile_dic[i])['results']['Functional'] == {}:
                del (scoreFile_dic[i])['results']['Functional']
        except Exception as e:
            pass
        try:
            delete_dic_values(dic_ideal['results']['Performance'], (scoreFile_dic[i])['results']['Performance'])
            if (scoreFile_dic[i])['results']['Performance'] == {}:
                del (scoreFile_dic[i])['results']['Performance']
        except Exception as e:
            pass

        if (scoreFile_dic[i])['results'] == {}:
            del (scoreFile_dic[i])['results']
    return dic_ideal

def delete_dic_values(dic_ideal, sub_dic):
    if dic_ideal == 'INVALID' or dic_ideal == None :
        del sub_dic
        return
    else:
        subsystem = dic_ideal.keys()
    for i in range(len(subsystem)):
        try:
            if dic_ideal[subsystem[i]] == 'INVALID' or dic_ideal[subsystem[i]] == None:
                if delete_in_dic(dic=sub_dic, key = subsystem[i]):
                    break
                continue
            else:
                scenario = dic_ideal[subsystem[i]].keys()
            for j in range(len(scenario)):
                try:
                    if dic_ideal[subsystem[i]][scenario[j]] == 'INVALID' or dic_ideal[subsystem[i]][scenario[j]] == None:
                        if delete_in_dic(dic=sub_dic, L1=subsystem[i], key =scenario[j]):
                            break
                        continue
                    else:
                        points_score = dic_ideal[subsystem[i]][scenario[j]].keys()
                    for k in range(len(points_score)):
                        try:
                            if dic_ideal[subsystem[i]][scenario[j]][points_score[k]] == 'INVALID' or dic_ideal[subsystem[i]][scenario[j]][points_score[k]] == None:
                                if delete_in_dic(dic = sub_dic,key = points_score[k],L1 = subsystem[i],L2 = scenario[j]):
                                    break
                                continue
                            else:
                                key = dic_ideal[subsystem[i]][scenario[j]][points_score[k]].keys()
                            for l in range(len(key)):
                                try:
                                    if dic_ideal[subsystem[i]][scenario[j]][points_score[k]][key[l]] == 'INVALID' or dic_ideal[subsystem[i]][scenario[j]][points_score[k]][key[l]] == None :
                                        if delete_in_dic(dic = sub_dic, key = key[l],L1 = subsystem[i],L2 = scenario[j],L3 = points_score[k]):
                                            break
                                except:
                                    pass
                        except:
                            pass
                except:
                    pass
        except Exception as e:
            pass
    return

def delete_in_dic(dic, key, L1 = None, L2 = None, L3 = None):
    try:
        flag = 0
        count = 0
        if L1:
            count += 1
            if L2:
                count += 1
                if L3:
                    count += 1
        if count == 3:
            if key in dic[L1][L2][L3]:
                del dic[L1][L2][L3][key]
            if dic[L1][L2][L3] == {}:
                del dic[L1][L2][L3]
                flag = 1
                count -= 1
        if count == 2:
            if key in dic[L1][L2]:
                del dic[L1][L2][key]
            if dic[L1][L2] == {}:
                del dic[L1][L2]
                flag = 1
                count -= 1
        if count == 1:
            if key in dic[L1]:
                del dic[L1][key]
            if dic[L1] == {}:
                del dic[L1]
                flag = 1
                count -= 1
        if count == 0:
            if key in dic:
                del dic[key]
            if dic == {}:
                del dic
                flag = 1
    except:
        pass
    return flag

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

def normalize_caliper():
    try:
        for files in glob.glob(os.path.join(caliper_path.HTML_DATA_DIR_OUTPUT, "*")):
            os.remove(files)
    except:
        pass
    try:
        normalize_caliper_output(caliper_path.HTML_DATA_DIR_INPUT)
    except Exception, e:
        logging.info(e.args[0], e.args[1])
        return

def normalize_caliper_output(yamlPath):
    for host_yaml_file in glob.glob(os.path.join(yamlPath,"*_score.yaml")):
        try:
            return_code = normalize_results( host_yaml_file)
        except Exception, e:
            logging.info(e)
            raise
        else:
            if return_code != 1:
                logging.info("there is wrong when dealing the yaml file")

def normalize_results(yaml_file):
    flag = 0
    results_str = 'results'
    perf_str = 'Performance'
    func_str = 'Functional'

    yaml_file_post = yaml_file[0:-5] + "_post" + yaml_file[-5:]
    fileName = yaml_file_post.split('/')[-1]
    yaml_file_post_output = os.path.join(caliper_path.HTML_DATA_DIR_OUTPUT,fileName)
    if os.path.exists(yaml_file):
        shutil.copyfile(yaml_file, yaml_file_post_output)
    else:
        logging.info("No such file %s" % yaml_file)
        flag = -1
        return flag
    fp = open(yaml_file)
    dic_ = yaml.load(fp)
    fp.close()

    if perf_str in dic_[results_str].keys():
        perf_results = dic_[results_str][perf_str]
        dic_[results_str][perf_str] = normalize_score(perf_results)
    if func_str in dic_[results_str].keys():
        func_results = dic_[results_str][func_str]
        dic_[results_str][func_str] = normalize_score(func_results)

    with open(yaml_file_post_output, 'w') as outfile:
        outfile.write(yaml.dump(dic_, default_flow_style=False))
        flag = 1
    outfile.close()
    return flag

def normalize_score(results):
    point_str = 'Point_Scores'
    total_str = 'Total_Scores'
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
                                if string.atof(x) >= 0]
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
