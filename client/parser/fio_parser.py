#!/usr/bin/env python

import re
import pdb
import string

def bw_parser(content, outfp):
    score = 0
    SEARCH_PAT = re.compile(r'bw\s*=\s*(\d+\.*\d*)B')
    pat_search = SEARCH_PAT.search(content)
    SEARCH_PAT_MB = re.compile(r'bw\s*=\s*(\d+\.*\d*)MB')
    pat_search_MB = SEARCH_PAT_MB.search(content)

    if pat_search:
        last_search = str(pat_search.group(1))
        last_search = string.atof(last_search) / 1024.0
        score = last_search
    elif pat_search_MB:
        last_search = str(pat_search_MB.group(1))
        last_search = string.atof(last_search) * 1024
        score = last_search
    else:
        SEARCH_PAT = re.compile(r'bw\s*=\s*(\d+\.*\d*)KB')
        last_search = SEARCH_PAT.search(content)
        outfp.write("bw:" + str(last_search.group(1)) + "KB/s\n")
        score = last_search.group(1)
    return score


def iops_parser(content, outfp):
    score = 0
    SEARCH_PAT = re.compile(r'iops\s*=\s*(\d+)')
    pat_search = SEARCH_PAT.search(content)
    outfp.write("bw:"+pat_search.group(1)+"\n")
    score = pat_search.group(1)
    return score

if __name__ == "__main__":
    infp = open("fio_output.log", 'r')
    outfp = open("tmp.log", "w+")
    content = infp.read()
    pdb.set_trace()
    bw_parser(content, outfp)
    iops_parser(content, outfp)
    outfp.close()
    infp.close()
