#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import string

def trans_float(minutes, seconds):
    total = string.atoi(minutes) * 60 + string.atof(seconds)
    return total

def time_parser(content, outfp):
    score = -1
    real = re.search("real(.*?)m(.*?)s\n", content)
    user = re.search("user(.*?)m(.*?)s\n", content)
    system_time = re.search("sys\s*(\d+)m(.*?)s\n", content)
    if real:
        real_time = trans_float(real.group(1), real.group(2))
        score = real_time
        outfp.write("real " + str(real_time) + "s\n")
    if user:
        user_time = trans_float(user.group(1), user.group(2))
        outfp.write("user " + str(user_time) + "s\n")
    if system_time:
        sys_time = trans_float(system_time.group(1), system_time.group(2))
        outfp.write("sys " + str(sys_time) + "s\n")
    return score

if __name__ == "__main__":
    infp = open("1.txt", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    time_parser(content, outfp)
    outfp.close()
    infp.close()
