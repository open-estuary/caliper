#!/usr/bin/python

import re
import string
import pdb


def compute_mflops(content, outfp):
    score = 0
    # pdb.set_trace()
    for lines in re.findall("Reps(.*?)\n(.*?)\n([\d\.\%\s]*)", content,
                            re.DOTALL):
        mflops = 0
        line = lines[2].strip().split("\n")
        for i in range(0, len(line)):
            if (line[i] != ""):
                try:
                    mflops_tmp = string.atof(line[i].strip().split(" ")[-1])
                except Exception, e:
                    print e
                    continue
                else:
                    mflops = mflops + mflops_tmp
        mflops = mflops/len(line)
        outfp.write(str(mflops) + "\n")
        score = mflops
    return score


def linpack_dp_parser(content, outfp):
    score = -1
    if re.search("LINPACK(.*?)Double(.*?)", content, re.DOTALL):
        score = compute_mflops(content, outfp)
    return score


def linpack_sp_parser(content, outfp):
    score = -1
    if re.search("LINPACK(.*?)Single(.*?)", content, re.DOTALL):
        score = compute_mflops(content, outfp)
    return score


if __name__ == "__main__":
    infp = open("2.txt", "r")
    outfp = open("3.txt", "a+")
    content = infp.read()
    pdb.set_trace()
    linpack_dp_parser(content, outfp)
    outfp.close()
    infp.close()
    infp = open("1.txt", "r")
    outfp = open("4.txt", "a+")
    content = infp.read()
    linpack_sp_parser(content, outfp)
    outfp.close()
    infp.close()
