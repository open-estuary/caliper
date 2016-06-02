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

def copydic(function, dic_ideal, dic_practical):
    #generate ideal template
    for key,value in function.iteritems():
        value(dic_ideal)
    for top,category in dic_practical.iteritems():
        if top == 'results':
            for category,sub_category in category.iteritems():
                for sub_category,scenario in sub_category.iteritems():
                    for scenario,key in scenario.iteritems():
                        for key,value in key.iteritems():
                            try:
                                dic_ideal[top][category][sub_category][scenario][key] = value
                            except:
                                print "%s %s %s %s %s" %(top,category,sub_category,scenario,key)
    return

def copydic_hardware(function, dic_ideal, dic_practical):
    # generate ideal template
    for key, value in function.iteritems():
        value(dic_ideal)
    for top, category in dic_practical.iteritems():
            for category, sub_category in category.iteritems():
                for sub_category, scenario in sub_category.iteritems():
                    try:
                        dic_ideal[top][category][sub_category]= scenario
                    except:
                        print "%s %s %s %s %s" % (top, category, sub_category)
    return

def delete(dic, option):
    del dic['results']['Functional']['peripheral']
    try:
            del dic['results']['Functional']['kernel']['EFIFS']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['posix']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['network']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['syscall']
    except KeyError:
            pass
    try:
            del dic['results']['Functional']['kernel']['vm']
    except KeyError:
            pass
    if option == "normalise" :
        try:
                del dic['results']['Performance']['application']['hadoop']['Point_Scores']['HadoopSleep']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['cpu']['Point_Scores']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['memory']['Point_Scores']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['file/vm']['Point_Scores']['Page_fault']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['rttest']['Point_Scores']['pi-stress']
        except KeyError:
                pass

    elif option == "report":
        try:
                del dic['results']['Performance']['application']['hadoop']['HadoopSleep']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['cpu']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Functional']['kernel']['memory']['hotplog']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['file/vm']['Page fault']
        except KeyError:
                pass
        try:
                del dic['results']['Performance']['latency']['rttest']['pi-stress']
        except KeyError:
                pass


def save(dicList):
    for dic in dicList:
        outputyaml = open("./Normalized_Files/"+dic['name']+"_score_post.yaml",'w')
        outputjson = open("./Normalized_Files/"+dic['name']+"_score_post.json",'w')
        outputyaml.write(yaml.dump(dic, default_flow_style=False))
        outputjson.write(json.dumps(dic))
        outputyaml.close()
        outputjson.close()


