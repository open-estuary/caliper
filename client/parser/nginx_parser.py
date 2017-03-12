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
    for wrps in re.findall("finished\s+in\s+.*?(\d+)\s+req[/]s.*?", content):
        wrps_final = string.atof(wrps.strip())
        outfp.write("wrps is %s \n" % wrps_final)
        wrps_final = float(wrps_final / 10000.0)
        dic['wrps'] = dic['wrps'] + wrps_final
	print dic
        flag = 1
    for dstat_data in re.findall("\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\d+\|.*?" , content):
	outfp.write("dstat data is %s \n" % dstat_data)
	key = "cpu_load" + str(i)
	cpu_load_dic[key] = dstat_data
	i = i + 1
	flag = 2
    if flag == 2:
	max_cpu_load = max(cpu_load_dic.iteritems(), key=operator.itemgetter(1))[0]
	dic['max_cpu_load'] = cpu_load_dic[max_cpu_load]
	print dic
    return dic

if __name__ == "__main__":
    infp = open("nginx_output.log", "r")
    content = infp.read()
    content = re.findall(r'<<<BEGIN TEST>>>(.*?)<<<END>>>',content,re.DOTALL)
    outfp = open("2.txt", "a+")
    for data in content:
        a = nginx_parser(data, outfp)
        #print a
    outfp.close()
    infp.close()
