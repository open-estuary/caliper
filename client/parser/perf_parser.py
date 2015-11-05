import re
import sys


def perf_parser(content, outfp):
    score = -1
    failNum = 0
    sucNum = 0
    skipNum = 0
    lines = content.splitlines()
    for line in lines:
        if re.search("\s:\sfail", line):
            failNum += 1
            outfp.write(line + '\n')
        elif re.search("\s:\spass", line):
            sucNum += 1
            outfp.write(line + '\n')
        elif re.search("\s:\sSkip", line):
            skipNum += 1
            outfp.write(line + '\n')
        else:
            # how to deal the 'Skip'
            continue
    if (failNum + sucNum + skipNum == 0):
        score = 0
    else:
        score = sucNum / (failNum + sucNum + skipNum + 0.0)
    return score

if __name__ == "__main__":
    fp = open(sys.argv[1], "r")
    text = fp.read()
    outfp = open("2.txt", "a+")
    perf_parser(text, outfp)
    fp.close()
    outfp.close()
