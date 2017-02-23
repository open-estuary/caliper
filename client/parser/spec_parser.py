#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import re
import logging
import yaml

def spec_parser(content,outfp):
    title0=re.findall('[ \t]*\[test:[ \t]*([0-9A-Za-z_]+)\]', content, re.M)
    if len(title0)!=1:
        logging.error("[%s] so many test cases" % (title0))
        return False

    title=title0[0]
    if re.search("_int_", title, re.IGNORECASE):
        title="sincore_int"
    elif re.search("_fp_", title, re.IGNORECASE):
        title="sincore_float"
    else:
        logging.error("[%s] unknow the parse type" % (title))
        return False

    value=re.findall('^[ \t]*[Ss]uccess[ \t]+([0-9.A-Za-z_]+)[ \t]+.*[ \t]+ratio=([0-9.]+),[ \t]+runtime=([0-9.]+),', content, re.M)
    dic={}
    dic[title]={}
    for s1 in value:
        name1=s1[0]
        dic[title][name1]=s1[1]

    if outfp:
        outfp.write(yaml.dump(dic,default_flow_style=False))
    else:
        logging.info(yaml.dump(dic,default_flow_style=False))

    return dic


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(filename)s[%(lineno)s]: %(message)s")
    str1='''
        [test: spec_int_1]
        Success 999.specrand base ref ratio=60.53, runtime=0.165197, power=0.00w, temp=0.00 deg, humidity=0.00%
        Success 483.xalancbmk base ref ratio=17.24, runtime=400.118959, power=0.00w, temp=0.00 deg, humidity=0.00%
        Success 400.perlbench base ref ratio=15.78, runtime=619.169026, power=0.00w, temp=0.00 deg, humidity=0.00%
    '''
    spec_parser(str1, None)
