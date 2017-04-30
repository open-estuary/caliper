#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import string

def get_average_value(content, option):
    score = 0
    sum_lat = 0
    i = 0
    if option == 1:
        option_string = 'Avg(.*?)Max'
    else:
        if option == 2:
            option_string = 'Avg:(.*?)us'

    for avgs_line in re.findall(option_string, content, re.DOTALL):
        avgs = avgs_line.split(":")[-1].strip().split(",")[0]
        tmp = string.atof(avgs.strip())
        sum_lat = sum_lat + tmp
        i = i + 1
    score = sum_lat / i
    return score

def rttest_parser(content, outfp):
    score = -1
    key_list = ['cyclictest', 'signaltest', 'pmqtest', 'sigwaittest',
                'svsematest', 'ptsematest', 'pmqtest']

    for key in key_list:
        if re.search(key, content):
            score = get_average_value(content, 1)
            outfp.write(key + ': ' + str(score) + ' us \n')
            return score

    if re.search('rt-migrate-test', content):
        score = get_average_value(content, 2)
        outfp.write('rt-migrate-test:  ' + str(score) + ' us\n')
    elif re.search('pi-stress', content):
        score = 0
        sum_time = 0
        for lines in re.findall("Test\s+Duration:(.*)", content, re.DOTALL):
            for values in re.findall("(\d+)", lines):
                tmp_value = values.strip()
                tmp_data = string.atof(tmp_value)
                sum_time = sum_time * 60 + tmp_data
        outfp.write("pi-stress:  " + str(sum_time) + " s\n")
    else:
        if re.search('hackbench', content):
            score = 0
            for values in re.findall("Time:(.*)", content):
                score = values.strip()
                if re.search("hackbench(.*?)-P", content) or\
                        re.search("--process", content):
                    outfp.write("hackbench process: " + score + " s\n")
                else:
                    if re.search("hackbench(.*?)-T", content) or \
                            re.search("--threads", content):
                        outfp.write("hackbench thread: " + score + ' s\n')
    return score

if __name__ == "__main__":
    infp = open("1.txt", "r")
    outfp = open("2.txt", "a+")
    contents = infp.read()
    for content in re.findall("%%%\s*test_start\s*\n(.*?)\n%%%\s*test_end",
                                contents, re.DOTALL):
        rttest_parser(content, outfp)

    outfp.close()
    infp.close()
