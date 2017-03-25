#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import string
import pdb

def iperf_parser(content, outfp, tag):
    score = -1
    sum_score = 0
    count = 0
    if (tag == 'iperf TCP'):
        if re.search('SUM', content):
            for speed in re.findall("\[SUM\].*?[MG]Bytes(.*?)MBytes/sec.*?sender", content):
                score = string.atof(speed.strip())
        else:
            for speed in re.findall("[MG]Bytes(.*?)MBytes/sec.*?sender", content):
                score = string.atof(speed.strip())
    else:
        if (tag == 'iperf UDP'):
            if re.search('SUM', content):
                for speed in re.findall("\[SUM\].*?[MG]Bytes(.*?)MBytes/sec.*?/.*?", content):
                    score = string.atof(speed.strip())
            else:
                for speed in re.findall("[MG]Bytes(.*?)MBytes/sec.*?/.*?", content):
                    score = string.atof(speed.strip())

    outfp.write("speed of %s is %.3f MBytes/sec\n" % (tag, score))

    return score * 8

def iperf_TCP_parser(content, outfp):
    return iperf_parser(content, outfp, 'iperf TCP')

def iperf_UDP_parser(content, outfp):
    return iperf_parser(content, outfp, 'iperf UDP')

if __name__ == "__main__":
    infp = open("iperf_output.log", "r")
    content = infp.read()
    content = re.findall(r'<<<BEGIN TEST>>>(.*?)<<<END>>>',content,re.DOTALL)
    outfp = open("2.txt", "a+")
    count = 0
    for data in content:
        if count < 8:
            iperf_TCP_parser(data, outfp)
        else:
            iperf_UDP_parser(data, outfp)
        count += 1
    outfp.close()
    infp.close()
