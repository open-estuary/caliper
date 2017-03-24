#!/usr/bin/python

import re
import string

def scimark_parser(content, outfp):
    score = -1
    m = re.search("Composite Score(.*?)\n", content)
    if m:
        score = 0
        line = m.group()
        outfp.write(line)
        score_tmp = line.strip().split(":")[-1].strip()
        try:
            score_latter = string.atof(score_tmp)
        except Exception, e:
            print e
        else:
            score = score_latter
        return score


if __name__ == "__main__":
    infp = open("1.ttx", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    scimark_parser(content, outfp)
    outfp.close()
    infp.close()
