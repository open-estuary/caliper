#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                      
#    E-mail    :    wu.wu@hisilicon.com 
#    Data      :    2015-10-31 14:27:40
#    Desc      :

import pdb
import re
import string

sysbench_dic = {}
response_times = {}

SYSBENCH_RESULT_NAME_LATENCY = 'sysbench latency'
NA_UNIT = 'NA'
SECONDS_UNIT = 'seconds'
MS_UNIT = 'milliseconds'

RESPONSE_TIME_TOKENS = ['min', 'avg', 'max', 'percentile']

def sysbench_parser(content, outfp):
    seen_general_statistics = False
    seen_response_time = False

    for line in content.splitlines():
        if re.search('General\s+statistics:', line):
            seen_general_statistics = True
            continue
        if seen_general_statistics:
            if re.match('^ +response time:.*', line):
                seen_response_time = True
                continue

        if seen_general_statistics and seen_response_time:
            for token in RESPONSE_TIME_TOKENS:
                search_string = '.*%s: +(.*)ms' % token
                if re.findall(search_string, line):
                    response_times[token] = float(re.findall(search_string, \
                            line)[0])
                    sysbench_dic[token] = response_times[token]
                    
    for token in RESPONSE_TIME_TOKENS:
        metric_name = '%s %s' % (SYSBENCH_RESULT_NAME_LATENCY, token)

        metric_name = '%s' % (metric_name)
        outfp.write(metric_name + '  ' + str( response_times[token]) + '  ' +\
                    MS_UNIT + '\n')
    return sysbench_dic

if __name__=="__main__":
    infp = open("1.txt", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    pdb.set_trace()
    sysbench_parser(content, outfp)
    outfp.close()
    infp.close()
