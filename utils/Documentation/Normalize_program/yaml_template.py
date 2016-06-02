#!/usr/bin/python
import openpyxl
import copy
import sys
import yaml
import dictionary
import pdb
import glob
import os
import json
from normalize import *
from report import *
from helper import *
from hw_test import *

path="./Report_input"
path_normalize="./Normalized_input"
path_hardware = "./HardwareInfo"
path_hardware_output = "./hardware_yaml"
dic = {}
testfunction = {
    '[cachebench]' : dictionary.cachebench,
    '[compile]' : dictionary.complie,
    '[coremark]' : dictionary.coremark,
    '[dhrystone]' : dictionary.dhrystone,
    '[ebizzy]' : dictionary.ebizzy,
    '[fio]' : dictionary.fio,
    '[hadoop]' : dictionary.hadoop, 
    '[iozone]' : dictionary.iozone,
    '[iperf]' : dictionary.iperf,
#    '[kselftest]' : dictionary.kselftest,
    '[linpack]' : dictionary.linpack,
    '[lmbench]' : dictionary.lmbench, 
    '[ltp]' : dictionary.ltp,
#    '[memtester]' : dictionary.memtester,
    '[nbench]' : dictionary.nbench,
    '[netperf]' : dictionary.netperf, 
    '[openssl]' : dictionary.openssl,
    '[perf]' : dictionary.perf,
    '[rttest]' : dictionary.rttest,
    '[tinymembench]' : dictionary.tinymembench,
    '[scimark]' : dictionary.scimark,
    '[scimarkJava]' : dictionary.scimarkJava,
    '[sysbench]' : dictionary.sysbench,
    '[unzip]' : dictionary.unzip
}


#open the test list file  
testlist = open("testList","r")

#delete the testlist from the dictionary 
for test in testlist:
    if test[0] == '#': 
       del testfunction[test[1:].strip()]


if sys.argv[1] == "-n":
    dicList = []
    for filename in glob.glob(os.path.join(path_normalize, '*.yaml')):
        dicList.append(yaml.load(open(filename)))
    normalize(testfunction,dicList)
    save(dicList)

if sys.argv[1] == "-r":
    dic_ideal = {}
    for key,value in testfunction.iteritems():
        value(dic_ideal)
    filelist=[]
    heading_list = ["SL NO", "TOOLS", "TopDimention", "Category", "Scenario", "Testcase"]
    generateReport("Consolidated.xlsx", "Consolidate", testfunction, heading_list)
   
    pos = len(heading_list) + 1
    size = len(heading_list) + 1
    for filename in glob.glob(os.path.join(path, '*.yaml')):
        filelist.append(filename)
    filelist.sort()
    for filename in glob.glob(os.path.join(path, '*.yaml')):
        dic_practical = yaml.load(open(filename))
        delete(dic_practical, "report")
        #generateReport(filename, testfunction, dic_practical)
        updateReport("Consolidated.xlsx","Consolidate",filename.split("/")[-1],pos, size, testfunction, copydic, dic_practical)
        pos = pos + 1

if sys.argv[1] == '-h':
    dic = {}
    filelist = []
    heading_list = ["SL NO", "Tools", "Category", "Sub-cases"]
    pos = len(heading_list) + 1
    size = len(heading_list) + 1
    for filename in glob.glob(os.path.join(path_hardware, '*_Targetinfo')):
        populate_yaml(filename,dic)
        update(dic,filename)
    generateReport("Hardware.xlsx", "Hardware", category, heading_list)
    for filename in glob.glob(os.path.join(path_hardware_output, '*.yaml')):
        filelist.append(filename)
    filelist.sort()
    for filename in filelist:
        print filename
        dic_practical = yaml.load(open(filename))
        updateReport("Hardware.xlsx","Hardware",filename.split("/")[-1], pos, size, category, copydic_hardware,dic)
        pos = pos + 1

