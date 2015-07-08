import os
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.conf import settings 

def get_files():
    json_dir = settings.DATAFILES_FOLDER
    filesname = []
    for root, dirs, files in os.walk(json_dir):
        for i in range(0, len(files)):
            if files[i].endswith('.json'):
                filesname.append( os.path.join(root, files[i]) )
    return filesname

def get_sum_dics(files):
    dic = {}
    dic['config'] = {}
    dic['test_tools'] = {}
    dic['summary'] = {}
    
    conf_tmp = {}
    tools_tmp = {}
    summary_tmp = {}
    for filename in files:
        with open(filename) as fp:
            data = json.load(fp)
        fp.close()
        target = filename.split('.')[0].split('/')[-1]
        conf_tmp[target] = data['Configuration']
        sum_tmp = {}
        perf_dic = data['results']['Performance']
        for key in perf_dic.keys():
            sum_tmp[key] = perf_dic[key]['Total_Scores']
        summary_tmp[target] = sum_tmp
    dic['config'] = conf_tmp
    dic['summary'] = summary_tmp
    return dic

def get_each_sum_item( files, category ):
    dic = {}
    for filename in files:
        tmp_dic = {}
        target = filename.split('.')[0].split('/')[-1]
        dic[target] = {}
        with open(filename) as fp:
            data = json.load(fp)
        fp.close()
        try:
            perf_dic = data['results']['Performance'][category]
            for key in perf_dic.keys():
                if (key != 'Total_Scores'):
                    tmp_dic[key] = perf_dic[key]['Total_Scores']
        except Exception:
            tmp_dic = {}
        dic[target] = tmp_dic
    return dic

def get_detail_data( files, category ):
    dic = {}
    dic['sum'] = get_each_sum_item(files, category)
    for filename in files:
        with open(filename) as fp:
            data = json.load(fp)
        fp.close()
        try:
            perf_dic = data['results']['Performance'][category]
            for key in perf_dic.keys():
                if (key != 'Total_Scores'):
                    dic[key] = {}
            break
        except Exception:
            dic = {}
    for key in dic.keys():
        if (key == 'Total_Scores' or key == 'sum'):
            continue
        tmp_dic = {}
        for filename in files:
            with open(filename) as fp:
                data = json.load(fp)
            fp.close()
            target = filename.split('.')[0].split('/')[-1]
            
            test_points = data['results']['Performance'][category][key]
            tmp_dic[target] = test_points['Point_Scores']
        dic[key] = tmp_dic
    return dic

def summary(request):
    files = get_files()
    dic_sum = get_sum_dics(files)
    return render(request, 'polls/summary.html', {'dic_sum': json.dumps(dic_sum)})

def algorithm(request):
    files = get_files()
    dic_alg = get_detail_data(files, 'algorithm')
    return render(request, 'polls/algorithm.html', 
            {'dic_alg': json.dumps(dic_alg)})

def cpu(request):
    files = get_files()
    dic_cpu = get_detail_data(files, 'cpu')
    return render(request, 'polls/cpu.html', {'dic_cpu': json.dumps(dic_cpu)})

def disk(request):
    files = get_files()
    dic_disk = get_detail_data(files, 'disk')
    return render(request, 'polls/disk.html', {'dic_disk': json.dumps(dic_disk)})

def latency(request):
    files = get_files()
    dic_lat = get_detail_data(files, 'latency')
    return render(request, 'polls/latency.html', {'dic_lat': json.dumps(dic_lat)})

def memory(request):
    files = get_files()
    dic_mem = get_detail_data(files, 'memory')
    return render(request, 'polls/memory.html', {'dic_mem': json.dumps(dic_mem)})

