##chenxiang c00284940
##chenxiang66@hisilicon.com

import re
import os
import pdb

def bw_parser(content,outfp):
   score = 0
   SEARCH_PAT = re.compile(r'bw\s*=\s*(\d+)')
   pat_search = SEARCH_PAT.search(content)
   #if pat_search:
   #   print pat_search.group(1)
   outfp.write("bw:"+pat_search.group(1)+"\n")
   score = pat_search.group(1)
   return score

def iops_parser(content,outfp):
   score = 0
   SEARCH_PAT = re.compile(r'iops\s*=\s*(\d+)')
   pat_search = SEARCH_PAT.search(content)
   #if pat_search:
   #   print pat_search.group(1)
   outfp.write("bw:"+pat_search.group(1)+"\n")
   score = pat_search.group(1)
   return score

if __name__ == "__main__":
   PATH = os.path.abspath("../..")
   infp = open(PATH+"/gen/x86_64/output/fio_output.log",'r')
   outfp = open("tmp.log","w+")
   content = infp.read()
   #bw_parser(content,outfp)
   iops_parser(content,outfp)
   outfp.close()
   infp.close()
