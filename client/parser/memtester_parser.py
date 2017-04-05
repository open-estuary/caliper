#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


def memtester_parser(content, outfp):
    flag = -1
    if re.search('fail', content):
        flag = 0
    else:
        flag = 1
    outfp.write('memtester:  %s\n' % flag)
    return flag


if __name__ == "__main__":
    infp = open("1.txt", "r")
    outfp = open("2.txt", "a+")
    contents = infp.read()
    for content in re.findall(
                    "%%%\s*test_start\s*\n(.*?)\n%%%\s*test_end",
                    contents,
                    re.DOTALL):
        memtester_parser(content, outfp)
    outfp.close()
    infp.close()
