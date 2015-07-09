import re
import sys

# how to test this part?
# sys:
# user:
# real:
def ebizzy_parser(content, outfp):
    dic = {}
    lines = content.splitlines()
    for line in lines:
        if re.search('real', line):
            dic['real'] = line.split()[1]
            outfp.write(line + '\n')
        elif re.search('user', line):
            dic['user'] = line.split()[1]
            outfp.write(line + '\n')
        elif re.search('sys', line):
            dic['sys'] = line.split()[1]
            outfp.write(line + '\n')
        else:
            if re.search('records', line):
                dic['records/s'] = line.split()[0]
                outfp.write(line + '\n')
    return dic

if __name__=="__main__":
    fp = open(sys.argv[1], "r")
    text = fp.read()
    outfp = open("2.txt", "a+")
    ebizzy_parser(text, outfp)
    fp.close()
    outfp.close()
