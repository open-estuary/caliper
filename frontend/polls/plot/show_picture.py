#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   wuyanjun 00291783
#   E-mail  :   wu.wu@hisilicon.com
#   Date    :   15/01/21 19:41:34
#   Desc    :
#

import os
import re
import yaml
import shutil
import logging

import parser_yaml_result as deal_result
from django.conf import settings

web_yamls_dir = settings.DATAFILES_FOLDER
polls_location = os.path.join(web_yamls_dir,"..", "..", "..", "polls", "static",
                                "polls", "pictures")
static_path = os.path.join(web_yamls_dir,"..", "..", "..", "polls","templates","polls")

static_files = ["Caliper-iteration.png","Caliper_report_clasification.JPG","Caliper_report_classification.JPG","Classification.png","percentile_calculation.PNG","flowchart.PNG"\
                    ,"iterative_execution.html","score_Calculation.html","Caliper_Test_Cases.html","caliper_report.css","Caliper_Test_cases.PNG"]
def get_targets_data(path):
    yaml_files = []
    for root, dirs, files in os.walk(path):
        for i in range(0, len(files)):
            if re.search('_score_post\.yaml', files[i]):
                yaml_name = os.path.join(root, files[i])
                yaml_files.append(yaml_name)
    return yaml_files


def show_caliper_result():
    file_lists = []
    filesname = get_targets_data(web_yamls_dir)
    files_new = []
    for i in range(0, len(filesname)):
        print i, filesname[i]
        fp = open(filesname[i])
        data = yaml.load(fp)
        data = data['Configuration']
        if data['Machine_arch'] == 'x86_64':
            files_new.append(filesname[i])
    files_new.sort()
    filesname = [i for i in filesname if not i in files_new]
    filesname.sort()
    files_new.sort()
    for i in files_new:
        filesname.append(i)
    picture_location = os.path.abspath(polls_location)

    if os.path.exists(picture_location):
        shutil.rmtree(picture_location)

    os.makedirs(picture_location)
    try:
        deal_result.draw_picture(filesname, picture_location)
        for files in static_files:
            shutil.copy(os.path.join(static_path,files), picture_location)
    except Exception:
        logging.info("There is wrong in drawing pictures")
