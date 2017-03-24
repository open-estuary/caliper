#!/usr/bin/env python

import re
import yaml

def parser(content, option, outfp):
    score = 0
    for lines in re.findall(
                    "=+LINUX\s+DATA\s+BELOW\s*=+\n(.*?)\n\*\s+Trademarks",
                    content,
                    re.DOTALL):
        if lines:
            line_list = lines.splitlines()
            for i in range(0, len(line_list)):
                if re.search("MEMORY\s+INDEX", line_list[i]):
                    memory_line = line_list[i]
                elif re.search("INTEGER\s+INDEX", line_list[i]):
                    int_line = line_list[i]
                else:
                    if re.search("FLOATING-POINT", line_list[i]):
                        float_line = line_list[i]
            if option == "int":
                line_list.remove(memory_line)
                line_list.remove(float_line)
                score = int_line.split(":")[1].strip()
            elif option == "float":
                line_list.remove(int_line)
                line_list.remove(memory_line)
                score = float_line.split(":")[1].strip()
            else:
                if option == "memory":
                    line_list.remove(int_line)
                    line_list.remove(float_line)
                    score = memory_line.split(":")[1].strip()

            for i in range(0, len(line_list)):
                outfp.write(line_list[i] + '\n')
            return score


def nbench_int_parser(content, outfp):
    score = -1
    score = parser(content, "int", outfp)
    return score


def nbench_float_parser(content, outfp):
    score = -1
    score = parser(content, "float", outfp)
    return score

dic = {}
dic['sincore_int'] = {}
dic['sincore_float'] = {}
int_list = ['NUMERIC SORT', 'STRING SORT', 'BITFIELD', 'FP EMULATION',
            'ASSIGNMENT', 'HUFFMAN', 'IDEA']
float_list = ['FOURIER', 'NEURAL NET', 'LU DECOMPOSITION']


def nbench_parser(content, outfp):
    for line in content.splitlines():
        get_value(line, 'sincore_int', int_list)
        get_value(line, 'sincore_float', float_list)
    outfp.write(yaml.dump(dic, default_flow_style=False))
    return dic


def get_value(line, flag, list_tables):
    for label in list_tables:
        if re.search(label, line):
            value = re.findall('(\d+\.*\d*)', line)[0]
            dic[flag][label] = value
            break

if __name__ == "__main__":
    infp = open("nbench_output.log", "r")
    outfp = open("2.txt", "a+")
    content = infp.read()
    # pdb.set_trace()
    nbench_parser(content, outfp)
    outfp.close()
    outfp = open("3.txt", "a+")
    # nbench__parser(content, outfp)
    outfp.close()
