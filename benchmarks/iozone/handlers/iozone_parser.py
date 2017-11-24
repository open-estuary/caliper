import re
import pdb


def parser(content, outfp):
    score = 0
    for version in re.findall("(Iozone:.*Version.*?)\s+\n", content,
                        re.DOTALL):
        outfp.write(version)
        outfp.write("\n")

    for results in re.findall("(File\s+size.*)", content, re.DOTALL):
        outfp.write(results)
        outfp.write("\n")

    keywords = ['write', 'rewrite', 'read', 'reread', 'random_read',
            'random_write', 'bkwd_read', 'recored_rewrite', 'stride_read',
            'fwrite', 'frewrite', 'fread', 'freread']
    dic = {'write': 0, 'rewrite': 0, 'read': 0, 'reread': 0, 'random_read': 0,
            'random_write': 0, 'bkwd_read': 0, 'recored_rewrite': 0,
            'stride_read': 0, 'fwrite': 0, 'frewrite': 0, 'fread': 0,
            'freread': 0}

    if re.search("iozone\s+test\s+complete", content):
        for line in re.findall("(\d+\s+\d+\s+\d+\s+.*?)\niozone\s+test",
                                content, re.DOTALL):
            fields = line.split()
            for i in range(0, len(keywords)):
                try:
                    score = fields[i+2]
                except Exception, e:
                    print e
                    score = 0
                dic[keywords[i]] = score
                outfp.write(keywords[i] + ": "+score+"\n")
    return dic


def iozone_parser(content, outfp):
    return parser(content, outfp)


if __name__ == "__main__":
    infp = open("iozone_output.log", "r")
    content = infp.read()
    outfp = open("2.txt", "a+")
    pdb.set_trace()
    # iozone_read_parser(content, outfp)
    # iozone_write_parser(content, outfp)
    # iozone_rw_parser(content, outfp)
    iozone_parser(content, outfp)
    outfp.close()
    infp.close()
