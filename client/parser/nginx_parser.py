import re
import string

#finished in 2 sec, 697 millisec and 187 microsec, 9268 req/s, 7693 kbyte/s
#requests: 25000 total, 25000 started, 25000 done, 25000 succeeded, 0 failed, 0 errored

def nginx_parser(content, outfp):
    result = 0
    flag = 0
    for wrps in re.findall("finished\s+in\s+.*?(\d+)\s+req[/]s.*?", content):
        wrps_final = string.atoi(wrps.strip())
        outfp.write("wrps is %s \n" % wrps_final)
        wrps_final = (wrps_final / 1000)
        result += wrps_final
        flag = 1
    if flag == 1:
        return result
    if flag == 0:
        return -1

if __name__ == "__main__":
    infp = open("nginx_output.log", "r")
    content = infp.read()
    content = re.findall(r'<<<BEGIN TEST>>>(.*?)<<<END>>>',content,re.DOTALL)
    outfp = open("2.txt", "a+")
    for data in content:
        a = nginx_parser(data, outfp)
        print a
    outfp.close()
    infp.close()
