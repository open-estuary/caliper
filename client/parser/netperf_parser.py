#!/usr/bin/env python

import re
import pdb


def common_parser(content, outfp, unit):
    score = -1
    lines = content.splitlines()

    test = re.findall('(.*)from', content)
    if test:
        test_case = test[0].strip()
        flag = 0
        for i in range(0, len(lines)):
            if flag == 1:
                break
            if re.search(unit, lines[i]):
                for j in range(i+1, len(lines)):
                    if ((len(lines[j].split()) >= 5) and
                            re.match('\d+', lines[j].split()[0])):
                        score = lines[j].split()[-1]
                        flag = 1
                        break
    	outfp.write(test_case + ' ' + str(score) + '\n')
    else:
        score = 0
    return score


def throughput_parser(content, outfp):
    return common_parser(content, outfp, 'Throughput')


def frequent_parser(content, outfp):
    return common_parser(content, outfp, 'Rate')

if __name__ == "__main__":
    infp = open("output.log", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    pdb.set_trace()
    throughput_parser(content, outfp)
    frequent_parser(content, outfp)
    outfp.close()
    infp.close()
