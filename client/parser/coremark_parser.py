#!/usr/bin/python

import re
import string


def coremark_parser(content, outfp):
    score = -1
    m = re.search("Iterations/Sec(.*?)\n", content)
    if m:
        score = 0
        lastline = content.splitlines()[-1]
        outfp.write(lastline + '\n')
        score_tmp = lastline.split(":")[-1].strip().split("/")[0]
        try:
            score_latter = string.atof(score_tmp)
        except Exception, e:
            print e
        else:
            score = score_latter
        return score

if __name__ == "__main__":
    infp = open("1.txt", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    coremark_parser(content, outfp)
    outfp.close()
    infp.close()
