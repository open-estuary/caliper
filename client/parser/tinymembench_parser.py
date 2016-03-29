import re
import sys
import math
import yaml
def tinyResult(content, outfp):
	score = 0
	sum = 1.0
	i = 0
	avg_bandwidth = 0.0
	dic = {}
	dic['tiny_bandwidth'] = {}
	dic['tiny_bandwidth']['C copy backwards']  = []
	dic['tiny_bandwidth']['C copy']  = []
	dic['tiny_bandwidth']['C copy prefetched 32B'] = []
	dic['tiny_bandwidth']['C copy prefetched 64B'] = []
	dic['tiny_bandwidth']['C 2-pass copy'] = []
	dic['tiny_bandwidth']['C 2-pass copy prefetched 32B']  = []
        dic['tiny_bandwidth']['C 2-pass copy prefetched 64B']  = []
        dic['tiny_bandwidth']['C fill'] = []
        dic['tiny_bandwidth']['standard memcpy']  = []
        dic['tiny_bandwidth']['standard memset']  = []
	dic['tiny_latency'] = {}
	dic['tiny_latency']['Hugepage single random read']= []
	dic['tiny_latency']['Hugepage dual random read'] = []
	dic['tiny_latency']['No Hugepage single random read'] = []
	dic['tiny_latency']['No Hugepage dual random read'] = []


	outfp.write('OPERATIONS\t\t\t\t\t:\tBANDWIDTH\n')
	


	outfp.write("%s\n" %(content.split("==========================================================================")[-3]))

	outfp.write('+++++++++++++++++++++++++++++MEMORY Latency+++++++++++++++++++++++++++++++++')
	outfp.write("%s\n" %(content.split("==========================================================================")[-1]))
	
	if len(re.findall("(\d+\.\d+\s*)",content.split("==========================================================================")[-3],re.DOTALL)):


		for item in re.findall("(\d+\.\d+\s*)",content.split("==========================================================================")[-3],re.DOTALL):
			item = int(item.split(".")[0])
			if item > 100:		
				i = i + 1
				#sum = math.sqrt(sum * item)a
				if i == 1:
					dic['tiny_bandwidth']['C copy backwards'] = item
				elif i == 2:
					dic['tiny_bandwidth']['C copy'] = item
				elif i == 3:
					dic['tiny_bandwidth']['C copy prefetched 32B'] = item 
				elif i == 4:
					dic['tiny_bandwidth']['C copy prefetched 64B'] = item
				elif i == 5:
					dic['tiny_bandwidth']['C 2-pass copy'] = item
				elif i == 6:
					dic['tiny_bandwidth']['C 2-pass copy prefetched 32B'] = item
				elif i == 7:
					dic['tiny_bandwidth']['C 2-pass copy prefetched 64B'] = item
				elif i == 8:
					dic['tiny_bandwidth']['C fill'] = item
				elif i == 9:
					dic['tiny_bandwidth']['standard memcpy'] = item
				elif i == 10:
					dic['tiny_bandwidth']['standard memset'] = item
				if i > 10:
					break
				
	sum = 1.0
	i = 0
	content1 = str(content.split("==========================================================================")[-1])
	final_list = re.findall("(\d+\.\d+\s*)",content1.split("block size : single random read / dual random read, [MADV_HUGEPAGE")[-2],re.DOTALL)
	#outfp.write(line)
	line = []*34
	for item in final_list:
		item = float(item)
		if item != 0:
			item = 100000/item
		line.append(item)
			
		
	lista = [line[12],line[14],line[16],line[18],line[20],line[22],line[24], line[26],line[28],line[30],line[32]]
	dic['tiny_latency']['Hugepage single random read'] = lista
	listb = [line[13],line[15] ,line[17],line[19],line[21],line[23],line[25],line[27] ,line[29] ,line[31],line[33]]
	dic['tiny_latency']['Hugepage dual random read'] = listb
	

	content1 = str(content.split("block size : single random read / dual random read, [MADV_HUGEPAGE")[-1])
        final_lis = re.findall("(\d+\.\d+\s*)",content1,re.DOTALL)
	line = []*34
	for item in final_list:
		item = float(item)
		if item != 0:
			item = 100000/item
		line.append(item)
	lista = [line[12],line[14],line[16],line[18],line[20],line[22],line[24], line[26],line[28],line[30],line[32]]
	dic['tiny_latency']['No Hugepage single random read'] = lista
	listb = [line[13],line[15] ,line[17],line[19],line[21],line[23],line[25],line[27] ,line[29] ,line[31],line[33]]
	dic['tiny_latency']['No Hugepage dual random read'] = listb


	outfp.write(yaml.dump(dic, default_flow_style=False))
	return dic
	    	

def tinymembench_parser(content, outfp):
	score = -1
	score = tinyResult(content, outfp)


	return score


if __name__ == "__main__":
    fp = open(sys.argv[1], "r")
    text = fp.read()
    outfp = open("2.txt", "a+")
    tinymembench_parser(text, outfp)
    fp.close()
    outfp.close()
