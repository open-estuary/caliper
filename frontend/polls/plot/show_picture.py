#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   wuyanjun 00291783
#   E-mail  :   wu.wu@hisilicon.com
#   Date    :   15/01/21 19:41:34
#   Desc    :  
#

import os
import sys
import re
import shutil
import stat
import logging
import pdb
import subprocess

import parser_yaml_result as deal_result
from django.conf import settings

web_yamls_dir = settings.DATAFILES_FOLDER
polls_location = os.path.join(web_yamls_dir, "..", "..", "polls", "static", "polls", 
    "pictures")

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
    file_lists = get_targets_data(web_yamls_dir)
    picture_location = os.path.abspath(polls_location)
    
    if os.path.exists(picture_location):
        shutil.rmtree(picture_location)

    os.makedirs(picture_location)
    try:
        return_code = deal_result.draw_picture(file_lists, picture_location)
    except Exception, e:
        logging.info("There is wrong in drawing pictures")
    
    
