import re
def stress_ng_parser(content,outfp):
    result = 0
    if re.search(r'stress-ng: info:\s+\[[0-9]+\]\scpu\s+\d+\s+(\d+\.\d+).*',content):
        real_time = re.search(r'stress-ng: info:\s+\[[0-9]+\]\scpu\s+\d+\s+(\d+\.\d+).*',content)
        result =  real_time.group(1)
    outfp.write(content)
    return result 

