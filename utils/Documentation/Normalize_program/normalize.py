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
def normalize(function, dicList):
    #generate ideal template
    dic_ideal = {}
    for key,value in function.iteritems():
        value(dic_ideal)
    newDic = dictionary.convertDic(dic_ideal)
    for top,category in newDic.iteritems():
        if top == 'results':
            for category,sub_category in category.iteritems():
                    for sub_category,scenario in sub_category.iteritems():
                        dic = {}
                        value_Sub = [] 
                        value_Sub_Normalize = []
                        index = 0
                        for dic in dicList:
                            try:
                                value_Sub.append(dic[top][category][sub_category]['Total_Scores'])
                            except KeyError:
                                value_Sub.append(0)
                        for value in value_Sub:
                            if max(value_Sub) > 0:
                                if value > 0:
                                    value_Sub_Normalize.append(round(100*value/max(value_Sub),2))
                                else:
                                    value_Sub_Normalize.append(0)
                            else:
                                value_Sub_Normalize.append(0)

                        for dic in dicList:
                            try:
                                dic[top][category][sub_category]['Total_Scores'] = value_Sub_Normalize[index]
                                index+=1
                            except KeyError:
                                pass 
                        for scenario,division in scenario.iteritems():
                            if scenario != "Total_Scores":
                                for division,key in division.iteritems():
                                    if division == "Total_Scores":
                                        dic = {}
                                        value_Sub_Normalize = []
                                        value_Sub = [] 
                                        index = 0
                                        for dic in dicList:
                                            try:
                                                value_Sub.append(dic[top][category][sub_category][scenario][division])
                                            except KeyError:
                                                value_Sub.append(0)
                                        for value in value_Sub:
                                            if max(value_Sub) > 0:
                                                if value > 0:
                                                    value_Sub_Normalize.append(round(100*value/max(value_Sub),2))
                                                else:
                                                    value_Sub_Normalize.append(0)
                                            else:
                                                value_Sub_Normalize.append(0)

                                        for dic in dicList:
                                            try:
                                                dic[top][category][sub_category][scenario][division] = value_Sub_Normalize[index]
                                                index+=1
                                            except KeyError:
                                                pass
                                    else:
                                        for key,value in key.iteritems():
                                            dic = {}
                                            value_Sub_Normalize = []
                                            value_Sub = [] 
                                            index = 0
                                            for dic in dicList:
                                                try:
                                                    value_Sub.append(dic[top][category][sub_category][scenario][division][key])
                                                except KeyError:
                                                    value_Sub.append(0)
                                            for value in value_Sub:
                                                if max(value_Sub) > 0:
                                                    if value > 0:
                                                        value_Sub_Normalize.append(round(100*value/max(value_Sub),2))
                                                    else:
                                                        value_Sub_Normalize.append(0)
                                                else:
                                                    value_Sub_Normalize.append(0)

                                            for dic in dicList:
                                                try:
                                                    dic[top][category][sub_category][scenario][division][key] = value_Sub_Normalize[index]
                                                    index+=1
                                                except KeyError:
                                                   pass 
    for dic in dicList:
            delete(dic, "normalise")

