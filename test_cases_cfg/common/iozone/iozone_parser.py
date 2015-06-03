import re
import pdb

def parser(content, outfp, option):
    score = 0
    for version in re.findall("(Iozone:.*Version.*?)\s+\n", content, re.DOTALL):
        outfp.write(version)
        outfp.write("\n")

    for results in re.findall("(File\s+size.*)", content, re.DOTALL):
        outfp.write(results)
        outfp.write("\n")

    keywords = ['write', 'rewrite', 'read', 'reread', 'random_read', 'random_write', 'bkwd_read',
                'recored_rewrite', 'stride_read', 'fwrite', 'frewrite', 'fread', 'freread']
    #value_loc = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 }

    if re.search("iozone\s+test\s+complete", content):
        #p re.findall("(\d+\s+\d+\s+\d+\s+.*?)\n",content, re.DOTALL)
        for line in re.findall("(\d\s+\d+\s+\d+\s+.*?)\niozone\s+test",content, re.DOTALL):
            fields = line.split()
            for i in range(0, len(keywords)):
                if option == keywords[i]:
                    try:
                        score = fields[i+2]
                        outfp.write(option + ": "+score+"\n")
                        break
                    except Exception, e:
                        print e
                        score = 0
            return score

def iozone_read_parser(content, outfp):
    score = -1
    score = parser(content, outfp, "read")
    return score
       
def iozone_write_parser(content, outfp):
    score = -1
    score = parser(content, outfp, "write")
    return score

def iozone_rw_parser(content, outfp):
    score = -1
    score = parser(content, outfp, "bkwd_read")
    return score

def iozone_parser(content, outfp):
    dic = {}
    dic['iozone_read'] = -1
    dic['iozone_read'] = iozone_read_parser(content, outfp)
    dic['iozone_write'] = -1
    dic['iozone_write'] = iozone_write_parser(content, outfp)
    dic['iozone_rw'] = -1
    dic['iozone_rw'] = iozone_rw_parser(content, outfp)
    print dic
    return dic

if __name__=="__main__":
    infp = open("iozone_output.log", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    pdb.set_trace()
    #iozone_read_parser(content, outfp)
    #iozone_write_parser(content, outfp)
    #iozone_rw_parser(content, outfp)
    iozone_parser(content, outfp)
    outfp.close()
    infp.close()
