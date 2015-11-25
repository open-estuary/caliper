#!/usr/bin/python

import pdb
import re
import yaml

hadoop_dic = {}


def hadoop_parser(content, outfp):
    for line in content.splitlines():
        try:
            key = re.match("Hadoop\w+", line).group()
        except AttributeError:
            continue
        if key and key not in hadoop_dic:
            line_cnt = 0
            sum_value = 0
            for line_str in content.splitlines():
                if re.search(key, line_str):
                    value = line.split()[-2]
                    if value and value != '0':
                        line_cnt += 1
                        sum_value += int(value)
            if line_cnt:
                hadoop_dic[key] = sum_value / line_cnt
            else:
                hadoop_dic[key] = 0
    outfp.write(yaml.dump(hadoop_dic, default_flow_style=False))
    return hadoop_dic

if __name__ == "__main__":
    infp = open("1.txt", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    pdb.set_trace()
    hadoop_parser(content, outfp)
    outfp.close()
    infp.close()
