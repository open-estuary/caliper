#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import string

tcp_bw_lat_label = ['qperf_tcp_bw_1B', 'qperf_tcp_bw_2B', 'qperf_tcp_bw_4B', 'qperf_tcp_bw_8B', 'qperf_tcp_bw_16B', 'qperf_tcp_bw_32B', 'qperf_tcp_bw_64B', 'qperf_tcp_bw_128B', 'qperf_tcp_bw_256B', 'qperf_tcp_bw_512B', 'qperf_tcp_bw_1K', 'qperf_tcp_bw_2K', 'qperf_tcp_bw_4K', 'qperf_tcp_bw_8K', 'qperf_tcp_bw_16K', 'qperf_tcp_bw_32K', 'qperf_tcp_bw_64K',
'qperf_tcp_lat_1B', 'qperf_tcp_lat_2B', 'qperf_tcp_lat_4B', 'qperf_tcp_lat_8B', 'qperf_tcp_lat_16B', 'qperf_tcp_lat_32B', 'qperf_tcp_lat_64B', 'qperf_tcp_lat_128B', 'qperf_tcp_lat_256B', 'qperf_tcp_lat_512B', 'qperf_tcp_lat_1K', 'qperf_tcp_lat_2K', 'qperf_tcp_lat_4K', 'qperf_tcp_lat_8K', 'qperf_tcp_lat_16K', 'qperf_tcp_lat_32K', 'qperf_tcp_lat_64K']

tcp_bw_lat_dic = {'qperf_tcp_bw_1B': 'TCP_bw_000001B',
                     'qperf_tcp_bw_2B': 'TCP_bw_000002B',
                     'qperf_tcp_bw_4B': 'TCP_bw_000004B',
                     'qperf_tcp_bw_8B': 'TCP_bw_000008B',
                     'qperf_tcp_bw_16B': 'TCP_bw_000016B',
                     'qperf_tcp_bw_32B': 'TCP_bw_000032B',
                     'qperf_tcp_bw_64B': 'TCP_bw_000064B',
                     'qperf_tcp_bw_128B': 'TCP_bw_000128B',
                     'qperf_tcp_bw_256B': 'TCP_bw_000256B',
                     'qperf_tcp_bw_512B': 'TCP_bw_000512B',
                     'qperf_tcp_bw_1K': 'TCP_bw_001000B',
                     'qperf_tcp_bw_2K': 'TCP_bw_002000B',
                     'qperf_tcp_bw_4K': 'TCP_bw_004000B',
                     'qperf_tcp_bw_8K': 'TCP_bw_008000B',
                     'qperf_tcp_bw_16K': 'TCP_bw_016000B',
                     'qperf_tcp_bw_32K': 'TCP_bw_032000B',
                     'qperf_tcp_bw_64K': 'TCP_bw_064000B',
                     'qperf_tcp_lat_1B': 'TCP_lat_000001B',
                     'qperf_tcp_lat_2B': 'TCP_lat_000002B',
                     'qperf_tcp_lat_4B': 'TCP_lat_000004B',
                     'qperf_tcp_lat_8B': 'TCP_lat_000008B',
                     'qperf_tcp_lat_16B': 'TCP_lat_000016B',
                     'qperf_tcp_lat_32B': 'TCP_lat_000032B',
                     'qperf_tcp_lat_64B': 'TCP_lat_000064B',
                     'qperf_tcp_lat_128B': 'TCP_lat_000128B',
                     'qperf_tcp_lat_256B': 'TCP_lat_000256B',
                     'qperf_tcp_lat_512B': 'TCP_lat_000512B',
                     'qperf_tcp_lat_1K': 'TCP_lat_001000B',
                     'qperf_tcp_lat_2K': 'TCP_lat_002000B',
                     'qperf_tcp_lat_4K': 'TCP_lat_004000B',
                     'qperf_tcp_lat_8K': 'TCP_lat_008000B',
                     'qperf_tcp_lat_16K': 'TCP_lat_016000B',
                     'qperf_tcp_lat_32K': 'TCP_lat_032000B',
                     'qperf_tcp_lat_64K': 'TCP_lat_064000B'}

def qperf_parser(content, outfp):
    score = -1
    dic = {}

    count = 1
    for speed in re.findall("bw\s+=\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("tcp_bw is %.3f MB/sec\n" % (score))
        if count == 1:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_1B']] = score
        if count == 2:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_2B']] = score
        if count == 3:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_4B']] = score
        if count == 4:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_8B']] = score
        if count == 5:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_16B']] = score
        if count == 6:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_32B']] = score
        if count == 7:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_64B']] = score
        if count == 8:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_128B']] = score
        if count == 9:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_256B']] = score
        if count == 10:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_512B']] = score
        if count == 11:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_1K']] = score
        if count == 12:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_2K']] = score
        if count == 13:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_4K']] = score
        if count == 14:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_8K']] = score
        if count == 15:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_16K']] = score
        if count == 16:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_32K']] = score
        if count == 17:
            dic[tcp_bw_lat_dic['qperf_tcp_bw_64K']] = score
        
        count += 1

    count = 1
    flag = 0
    for speed_t in re.findall("latency\s+=\s+(.*?\s+.*)", content):
        if re.search('ms', speed_t):
            flag = 1
        speed_s = re.search('(.*?)\s+[mu]s', speed_t)
        speed = speed_s.group(1)
        score = string.atof(speed.strip())
        if flag == 1:
           score = score * 1000
        outfp.write("tcp_lat is %.3f us\n" % (score))
        if count == 1:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_1B']] = score
        if count == 2:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_2B']] = score
        if count == 3:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_4B']] = score
        if count == 4:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_8B']] = score
        if count == 5:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_16B']] = score
        if count == 6:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_32B']] = score
        if count == 7:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_64B']] = score
        if count == 8:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_128B']] = score
        if count == 9:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_256B']] = score
        if count == 10:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_512B']] = score
        if count == 11:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_1K']] = score
        if count == 12:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_2K']] = score
        if count == 13:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_4K']] = score
        if count == 14:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_8K']] = score
        if count == 15:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_16K']] = score
        if count == 16:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_32K']] = score
        if count == 17:
            dic[tcp_bw_lat_dic['qperf_tcp_lat_64K']] = score
        
        count += 1

    return dic
