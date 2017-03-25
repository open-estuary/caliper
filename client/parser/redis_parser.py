import re
import string
import pdb

def redis_parser(content , outfp ):
#[test: Instance_2]

    for test_case in re.findall("\[test:\s+(.*?)\]", content):
	test_case_latency = test_case + "_latency"
	test_case_bandwidth = test_case + "_bandwidth"
  
    dic = {}
    dic[test_case_latency] = {}
    dic[test_case_bandwidth] = {}
    dic[test_case_latency]['short-lat'] = 0
    dic[test_case_latency]['basic-lat'] = 0
    dic[test_case_latency]['pipeline-lat'] = 0
    dic[test_case_bandwidth]['short-qps'] = 0
    dic[test_case_bandwidth]['basic-qps'] = 0
    dic[test_case_bandwidth]['pipeline-qps'] = 0

    short_count = 0
    basic_count = 0
    pipeline_count = 0
    for contents in re.findall("====== SHORT ======.*?(\d+.\d+)\s+requests per second", content, re.DOTALL):
         short_final = string.atof(contents.strip())
         outfp.write("short-qps = %s \n " %  short_final)
         dic[test_case_bandwidth]['short-qps'] += short_final

    for contents in re.findall("====== BASIC ======.*?(\d+.\d+)\s+requests per second", content, re.DOTALL):
        basic_final = string.atof(contents.strip())
        outfp.write("basic-qps = %s \n " % basic_final)
        dic[test_case_bandwidth]['basic-qps'] += basic_final

    for contents in re.findall("====== PIPELINE ======.*?(\d+.\d+)\s+requests per second", content, re.DOTALL):
        pipeline_final = string.atof(contents.strip())
        outfp.write("pipeline-qps = %s \n\n " % pipeline_final)
        dic[test_case_bandwidth]['pipeline-qps'] += pipeline_final

    for contents in re.findall("====== SHORT ======.*?[9][0-9]\..*?%\s<=\s(\d+)\s+milliseconds", content, re.DOTALL):
        short_final = string.atof(contents.strip())
        outfp.write("short-lat = %s \n " %  short_final)
        dic[test_case_latency]['short-lat'] += short_final
	short_count += 1

    for contents in re.findall("====== BASIC ======.*?[9][0-9]\..*?%\s<=\s(\d+)\s+milliseconds", content, re.DOTALL):
        basic_final = string.atof(contents.strip())
        outfp.write("basic-lat = %s \n " % basic_final)
        dic[test_case_latency]['basic-lat'] += basic_final
	basic_count += 1

    for contents in re.findall("====== PIPELINE ======.*?[9][0-9]\..*?%\s<=\s(\d+)\s+milliseconds", content, re.DOTALL):
        pipeline_final = string.atof(contents.strip())
        outfp.write("pipeline-lat = %s \n\n " % pipeline_final)
        dic[test_case_latency]['pipeline-lat'] += pipeline_final
	pipeline_count += 1

    if short_count != 0:
    	dic[test_case_latency]['short-lat'] = dic[test_case_latency]['short-lat'] / short_count

    if basic_count != 0:
    	dic[test_case_latency]['basic-lat'] = dic[test_case_latency]['basic-lat'] / basic_count

    if pipeline_count != 0:
    	dic[test_case_latency]['pipeline-lat'] = dic[test_case_latency]['pipeline-lat'] / pipeline_count

    if dic[test_case_bandwidth]['short-qps'] == 0:
	dic[test_case_bandwidth]['short-qps'] = -1

    if dic[test_case_bandwidth]['basic-qps'] == 0:
	dic[test_case_bandwidth]['basic-qps'] = -1

    if dic[test_case_bandwidth]['pipeline-qps'] == 0:
	dic[test_case_bandwidth]['pipeline-qps'] = -1

    if dic[test_case_latency]['short-lat'] == 0:
	dic[test_case_latency]['short-lat'] = -1

    if dic[test_case_latency]['basic-lat'] == 0:
	dic[test_case_latency]['basic-lat'] = -1

    if dic[test_case_latency]['pipeline-lat'] == 0:
	dic[test_case_latency]['pipeline-lat'] = -1

    return dic

if __name__ == "__main__":
    infp = open("redis_output.log", "r")
    content = infp.read()
    content = re.findall(r'<<<BEGIN TEST>>>(.*?)<<<END>>>',content,re.DOTALL)
    outfp = open("2.txt", "a+")
    for data in content:
        a = redis_parser(data, outfp)
    outfp.close()
    infp.close()
