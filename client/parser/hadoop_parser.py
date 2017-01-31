#!/usr/bin/python

import pdb
import re
import yaml

#hadoop_dic = {}
#dfsio_testcases=['HadoopDfsioe-Write','HadoopDfsioe-read']

#def hadoop_parser(content,outfp):
#      try:
 #        list = re.findall(r'<<<BEGIN TEST>>>(.*?)<<<END>>>',content,re.DOTALL)
 #     except AttributeError:
  #           print "Tehre is something error with outputlog"

  #       if list:
   #           for lists in list:
    #             hadoop_parser_config(str(lists),outfp)


def hadoop_parser(content, outfp):
        hadoop_dic = {}
	dfsio_testcases=['HadoopDfsioe-Write','HadoopDfsioe-read']
        dimension=None	
	dims=re.findall("\[test:\shadoop_conf\d+\]",content)
        if dims:
           for dim in dims:
               dimension =dim.partition('[')[-1].rpartition(']')[0].split(':')[-1].strip()
               hadoop_dic[dimension+'_duration'] = {}
               hadoop_dic[dimension+'_throughput'] = {}

	for line in content.splitlines():
		try:
                   dim=re.match("\[test:\shadoop_conf\d+\]",line).group()
	           dimension =dim.partition('[')[-1].rpartition(']')[0].split(':')[-1].strip()
                   print "dimension"
                   print dimension
        	   hadoop_dic[dimension+'_duration'] = {}
        	   hadoop_dic[dimension+'_throughput'] = {}
	        except AttributeError:
		       pass

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
			   value = line.split()[-3]
		           if value and value != '0':
			      hadoop_dic[dimension+'_duration'][key] = value
			   else:
	        	      hadoop_dic[dimension+'_duration'][key] = 0

			   value = line.split()[-2]
		           if value and value != '0':
			      hadoop_dic[dimension+'_throughput'][key] = value
			   else:
	        	      hadoop_dic[dimension+'_throughput'][key] = 0
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
				hadoop_dic[dimension+'_throughput'][dfsio_testcases[0]]=(float(values[5]))*1024*1024

                    keys   = re.findall("Test exec time sec.*",data)
                    for key in keys:
                        #print key
                        values = key.split()
                        #for value in values:
                          #print value
                        if values:
                                hadoop_dic[dimension+'_duration'][dfsio_testcases[0]]=values[-1]

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
				hadoop_dic[dimension+'_throughput'][dfsio_testcases[1]]=(float(values[5]))*1024*1024
		    keys   = re.findall("Test exec time sec.*",data)
                    for key in keys:
                        #print key
                        values = key.split()
                        #for value in values:
                          #print value
                        if values:
                                hadoop_dic[dimension+'_duration'][dfsio_testcases[1]]=values[-1] 
	#print hadoop_dic
    	outfp.write(yaml.dump(hadoop_dic, default_flow_style=False))
    	return hadoop_dic

if __name__ == "__main__":
    infp = open("1.txt", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
#    pdb.set_trace()
    hadoop_parser(content, outfp)
    outfp.close()
    infp.close()

