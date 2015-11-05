# henxiang c00284940
# chenxiang66@hisilicon.com

import re
import pdb
import string


def bw_parser(content, outfp):
    score = 0
    SEARCH_PAT = re.compile(r'bw\s*=\s*(\d+\.*\d*)B')
    pat_search = SEARCH_PAT.search(content)

    if pat_search:
        last_search = string.atof(pat_search.group(1)) / 1024.0
    else:
        SEARCH_PAT = re.compile(r'bw\s*=\s*(\d+\.*\d*)KB')
        last_search = SEARCH_PAT.search(content)
    if last_search:
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
