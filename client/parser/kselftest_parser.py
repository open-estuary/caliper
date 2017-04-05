#!/usr/bin/python

import re
import pdb

def parser(content, outfp):
    score = -1
    fail = 0
    passd = 0
    skipd = 0
    for line in content.splitlines():
        if re.search("cd\s+.*echo", line):
            continue
        if re.search(":\s+\[SKIP\]", line) or re.search(":\s+skip", line):
            skipd += 1
            outfp.write(line + '\n')
        elif re.search(":\s+\[FAIL\]", line) or re.search(":\s+fail", line):
            fail += 1
            outfp.write(line + '\n')
        elif re.search(":\s+\[PASS\]", line) or re.search(":\s+pass", line):
            passd += 1
            outfp.write(line + '\n')
        elif re.search("FAIL", line):
            fail += 1
            outfp.write(line + '\n')
        else:
            if re.search("PASS", line):
                passd += 1
                outfp.write(line + '\n')

    summ = fail + passd + skipd
    if (summ != 0):
        score = passd / (summ+0.0)
    return score

if __name__ == "__main__":
    infp = open("kselftest_output.log", "r")
    outfp = open("3.txt", "a+")
    content = infp.read()
    pdb.set_trace()
    parser(content, outfp)
    outfp.close()
    infp.close()
