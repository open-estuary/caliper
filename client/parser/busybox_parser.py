#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def busybox_parser(content, outfp):
    flag = -1

    if re.search('succeed', content):
        flag = 1
    else:
        flag = 0
    outfp.write('busybox: %s\n' % flag)
    print flag
    return flag

if __name__ == "__main__":
    infp = open("1.txt", "r")
    outfp = open("2.txt", "a+")
    contents = infp.read()
    for content in re.findall(
            "%%%\s*test_start\s*\n(.*?)\n%%%\s*test_end",
            contents, re.DOTALL):
        busybox_parser(content, outfp)
    outfp.close()
    infp.close()
