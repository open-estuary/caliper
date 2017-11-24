import re
import string
import pdb
import sys


def get_average_value(content, outfp, flag_str):
    score = -1
    if re.search(flag_str, content):
        score = 0
        sum_value = 0
        i = 0
        for line in re.findall("(\d+\s+\d+\.\d+\s*)\n", content, re.DOTALL):
            tmp_data = line.split()[-1]
            try:
                tmp_value = string.atof(tmp_data)
            except Exception, e:
                print e
                continue
            else:
                sum_value = sum_value + tmp_value
                i = i + 1
        try:
            score = sum_value / i
        except Exception, e:
            print e
            score = 0
        return score


def cachebench_read_parser(content, outfp):
    score = -1
    score = get_average_value(content, outfp, "cachebench(.*)-r")
    outfp.write("read bandwidth: " + str(score) + '\n')
    return score


def cachebench_write_parser(content, outfp):
    score = -1
    score = get_average_value(content, outfp, "cachebench(.*)-w")
    outfp.write("write bandwidth: " + str(score) + '\n')
    return score


def cachebench_modify_parser(content, outfp):
    score = -1
    score = get_average_value(content, outfp, "cachebench(.*)-b")
    outfp.write("read/mdify/write bandwidth: " + str(score) + '\n')
    return score

if __name__ == "__main__":
    infp = open(sys.argv[1], "r")
    conten = infp.read()
    outfp = open("2.txt", "a+")
    pdb.set_trace()
    cachebench_read_parser(conten, outfp)
    outfp.close()
    infp.close()
