#!/usr/bin/python

import pdb
import re
import yaml

hadoop_dic = {}
dfsio_testcases=['HadoopDfsioe-Write','HadoopDfsioe-read']

def hadoop_parser(content, outfp):
	for line in content.splitlines():
		try:
		    match = re.match("Hadoop\w+\s+(\d+[-:.]*\s*)+", line).group()
		    print match
		except AttributeError:
		    continue
		if match:
			try:
				key=re.match("Hadoop\w+",match).group()
			except AttributeError:
			  continue
                        if key and key not in hadoop_dic:
			   value = line.split()[-2]
		           if value and value != '0':
			      hadoop_dic[key] = int(value)
			   else:
	        	      hadoop_dic[key] = 0
	datas = re.findall(r'start HadoopDfsioe-write bench(.*?)finish HadoopDfsioe-write bench', content, re.DOTALL)
		#print datas
	if datas:
		for data in datas:
		    #print data
		    keys   = re.findall("Average of Aggregated.*",data)
		    for key in keys:
			#print key
			values = key.split()
			#for value in values:
			  #print value
     			if values:
				hadoop_dic[dfsio_testcases[0]]=(float(values[5]))*1024*1024
	#print hadoop_dic
	datas = re.findall(r'start HadoopDfsioe-read bench(.*?)finish HadoopDfsioe-read bench', content, re.DOTALL)
	if datas:
        	for data in datas:
		    #print data
		    keys   = re.findall("Average of Aggregated.*",data)
		    for key in keys:
			#print key
			values = key.split()
			#for value in values:
				#print value
			if values:
				hadoop_dic[dfsio_testcases[1]]=(float(values[5]))*1024*1024
	#print hadoop_dic
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

