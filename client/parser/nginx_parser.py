#!/usr/bin/env python
import re
import string
import operator

#finished in 2 sec, 697 millisec and 187 microsec, 9268 req/s, 7693 kbyte/s
#requests: 25000 total, 25000 started, 25000 done, 25000 succeeded, 0 failed, 0 errored

def nginx_parser(content, outfp):
    dic = {}
    dic['wrps'] = 0
    dic['max_cpu_load'] = 0

    cpu_load_dic = {}
    i = 0
    flag = 0

    for contents in re.findall("finished in(.*?)\s+errored", content, re.DOTALL):
	fail_count = re.search(r'.*?(\d+)\s+failed.*?', contents)

	counts = fail_count.group(1)
	if counts == "0":
    	    for wrps in re.findall("\s+.*?(\d+)\s+req[/]s.*?", contents):
                wrps_final = string.atof(wrps.strip())
                outfp.write("wrps is %s \n" % wrps_final)
                wrps_final = float(wrps_final / 10000.0)
                dic['wrps'] = dic['wrps'] + wrps_final
                flag = 1

    for dstat_data in re.findall("\s+\d+\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\|.*?" , content):
	outfp.write("dstat data is %s \n" % dstat_data)
	key = "cpu_load" + str(i)
	cpu_load_dic[key] = string.atoi(dstat_data.strip())
	i = i + 1
	flag = 2
    if flag == 2:
	max_cpu_load = min(cpu_load_dic.iteritems(), key=operator.itemgetter(1))[1]
	dic['max_cpu_load'] = 100 - max_cpu_load
    if dic['wrps'] == 0 or dic['max_cpu_load'] == 0:
        dic = {}

    return dic

if __name__ == "__main__":
    infp = open("weighttp_client_1_output.log", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    for data in content:
        a = nginx_parser(data, outfp)
        #print a
    
    outfp.close()
    infp.close()
