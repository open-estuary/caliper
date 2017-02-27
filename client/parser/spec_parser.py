#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import logging
import yaml

def spec_parser(content,outfp):
    dic={}
    title0=re.findall('[ \t]*\[test:[ \t]*([0-9A-Za-z_]+)\]', content, re.M)
    if len(title0)!=1:
        logging.error("[%s] so many test cases" % (title0))
        return dic

    title=title0[0]
    s1=re.search("_(?P<tIF>int|fp|float)_(?P<tNo>[0-9]+)", title, re.IGNORECASE)
    if s1 == None:
        logging.error("[%s] the title is wrong" % (title))
        return dic

    if re.search("int", s1.group("tIF"), re.IGNORECASE):
        title="_int"
    elif re.search("(fp|float)", s1.group("tIF"), re.IGNORECASE):
        title="_float"
    else:
        logging.error("[%s] unknow the parse type" % (title))
        return dic

    if s1.group("tNo") > "1":
        title="multicore_"+s1.group("tNo")+title
    else:
        title="sincore"+title

    #logging.info("title[%s]" % (title))

    value=re.findall('^[ \t]*[Ss]uccess[ \t]+([0-9.A-Za-z_]+)[ \t]+.*[ \t]+ratio=([0-9.]+),[ \t]+runtime=([0-9.]+),', content, re.M)
    dic[title]={}
    for s1 in value:
        name1=s1[0]
        dic[title][name1]=s1[1]

    value=re.findall('^[ \t]*runspec finished at .*;[ \t]*([0-9]+)[ \t]+(total) seconds elapsed[ \t]*$', content, re.M)
    for s1 in value:
        name1=s1[1]
        dic[title][name1]=s1[0]

    if outfp:
        outfp.write(yaml.dump(dic,default_flow_style=False))
    else:
        logging.info(yaml.dump(dic,default_flow_style=False))

    return dic


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(filename)s[%(lineno)s]: %(message)s")
    str1='''
        [test: spec_fp_64]
        Success 999.specrand base ref ratio=60.53, runtime=0.165197, power=0.00w, temp=0.00 deg, humidity=0.00%
        Success 483.xalancbmk base ref ratio=17.24, runtime=400.118959, power=0.00w, temp=0.00 deg, humidity=0.00%
        Success 400.perlbench base ref ratio=15.78, runtime=619.169026, power=0.00w, temp=0.00 deg, humidity=0.00%
        runspec finished at Sat Feb 25 11:15:28 2017; 8200 total seconds elapsed
    '''
    spec_parser(str1, None)

