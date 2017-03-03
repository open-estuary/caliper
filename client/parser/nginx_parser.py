import re
import string

#finished in 2 sec, 697 millisec and 187 microsec, 9268 req/s, 7693 kbyte/s
#requests: 25000 total, 25000 started, 25000 done, 25000 succeeded, 0 failed, 0 errored

def nginx_parser(content, outfp):
    result = -1
    for requests in re.findall("requests:\s+\d+\s+total[,]\s+\d+\s+started[,]\s+\d+\s+done[,]\s+(.*?)\s+succeeded.*?", content):
        requests_final = string.atof(requests.strip())
        if requests_final != 0.0:
            for wrps in re.findall("finished\s+in\s+.*?(\d+)\s+req[/]s.*?", content):
                wrps_final = string.atof(wrps.strip())
                wrps_final = float(wrps_final / 10000)
                outfp.write("wrps is %s \n" % wrps_final)
                result = wrps_final
    return result

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
