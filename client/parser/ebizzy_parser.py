import re
import sys
import pdb


def ebizzy_records_parser(content, outfp):
    dic = {}
    dic['ebizzy_mmap_records'] = {}
    dic['ebizzy_no_mmap_records'] = {}

    thread_num = 0
    blocks = content.split("log:")
    flag = '_M'
    for block in blocks:
        if re.search('-M', block):
            dic_tmp = dic['ebizzy_no_mmap_records']
            flag = '_M'
        if re.search('-m', block):
            dic_tmp = dic['ebizzy_mmap_records']
            flag = '_m'
        for thread in re.findall('-t\s*(\d+)\s*', block):
            if int(thread) < int(10):
                thread = '0' + str(thread)
            thread_num = thread

        if not thread_num:
            continue

        if re.search('records\/s', block):
            list_value = ['records', thread_num]
            key = '_'.join(list_value)
            num = re.search('(\d+)\s*records\/s', block).group(1)
            dic_tmp[key] = num
            outfp.write(key + flag + ' ' + num + '\n')
    return dic


def ebizzy_sys_parser(content, outfp):
    dic = {}
    dic['ebizzy_mmap_time'] = {}
    dic['ebizzy_no_mmap_time'] = {}

    blocks = content.split("log:")
    thread_num = 0
    flag = '_M'
    for block in blocks:
        if re.search('-M', block):
            dic_tmp = dic['ebizzy_no_mmap_time']
            flag = '_M'
        if re.search('-m', block):
            dic_tmp = dic['ebizzy_mmap_time']
            flag = '_m'
        for thread in re.findall('-t\s*(\d+)\s*', block):
            if int(thread) < int(10):
                thread = '0' + str(thread)
            thread_num = thread

        if not thread_num:
            continue

        if re.search('sys', block):
            list_value = ['sys', thread_num]
            key = '_'.join(list_value)
            num = re.search('sys\s*(\d+\.*\d*)\s*s', block).group(1)
            dic_tmp[key] = num
            outfp.write(key + flag + '  ' + num + 's\n')
    return dic

if __name__ == "__main__":
    fp = open(sys.argv[1], "r")
    text = fp.read()
    pdb.set_trace()
    outfp = open("2.txt", "a+")
    ebizzy_records_parser(text, outfp)
    ebizzy_sys_parser(text, outfp)
    fp.close()
    outfp.close()
