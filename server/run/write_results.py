#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    E-mail    :    wu.wu@hisilicon.com
#    Data      :    2015-05-03 16:44:39
#    Desc      :
import os
import yaml
import logging
import string
import types

try:
    import caliper.common as common
except Exception:
    import common

from caliper.server.compute_model import scores_method
from caliper.server.compute_model.scores_method import Scores_method


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


def write_dic(result, tmp, score_way, yaml_file, score_yaml_file):
    flag = 0
    for key in result.keys():
        if type(result[key]) == dict:
            sub_dic = result[key]
            tmp.append(key)
            flag = write_sin_dic(sub_dic, tmp, score_way, yaml_file,
                                    score_yaml_file)
            tmp.remove(key)
        else:
            logging.debug("There is wrong with the parser")
            flag = -1
            return flag
    flag = 1
    return flag


def write_sin_dic(result, tmp, score_way, yaml_file, score_yaml_file):
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
        flag1 = write_yaml_perf(yaml_file, tmp, geo_mean)
        result_score = compute_score(score_way, geo_mean)
        flag2 = write_yaml_perf(score_yaml_file, tmp, result_score, 2)
        tmp.remove(key)
        if not flag1 & flag2:
            return flag1 & flag2
    flag = 1
    return flag


def write_multi_dic(result, tmp, score_way, yaml_file, score_yaml_file):
    flag = 0
    for key in result.keys():
        if type(result[key]) == dict:
            try:
                sub_dic = result[key]
                tmp.append(key)
                flag = write_dic(sub_dic, tmp, score_way, yaml_file,\
                                    score_yaml_file)
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
    if not os.path.exists(yaml_file):
        os.mknod(yaml_file)
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
