import os
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views import generic
from django.conf import settings
from plot import show_picture

CONFIG_STR = 'Configuration'
TOTAL_STR = 'Total_Scores'
POINT_STR = 'Point_Scores'
PERF_STR = 'Performance'
FUNC_STR = 'Functional'
RESULTS_STR = 'results'

def get_files():
    json_dir = settings.DATAFILES_FOLDER
    filesname = []
    for root, dirs, files in os.walk(json_dir):
        for i in range(0, len(files)):
            if files[i].endswith('.json'):
                filesname.append( os.path.join(root, files[i]) )
    return filesname

def get_eachItem_sum(files, testItem):
    summary_tmp = {}
    for filename in files:
        with open(filename) as fp:
            data = json.load(fp)
        fp.close()
        target = '_'.join(filename.split('/')[-1].split('_')[:-2])
        sum_tmp = {}
        if testItem in data[RESULTS_STR].keys():
            sum_dic = data[RESULTS_STR][testItem]
        else:
            return {}
        for key in sum_dic.keys():
            sum_tmp[key] = sum_dic[key][TOTAL_STR]
        summary_tmp[target] = sum_tmp
    return summary_tmp

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
        target = '_'.join(filename.split('/')[-1].split('_')[:-2])
        conf_tmp[target] = data[CONFIG_STR]
    dic['config'] = conf_tmp
    dic['perf_summary'] = get_eachItem_sum(files, PERF_STR)
    dic['func_summary'] = get_eachItem_sum(files, FUNC_STR)
    return dic

def get_each_sum_item( files, testItem, category ):
    dic = {}
    for filename in files:
        tmp_dic = {}
        target = '_'.join(filename.split('/')[-1].split('_')[:-2])
        dic[target] = {}
        with open(filename) as fp:
            data = json.load(fp)
        fp.close()
        try:
            perf_dic = data[RESULTS_STR][testItem][category]
            for key in perf_dic.keys():
                if (key != TOTAL_STR):
                    tmp_dic[key] = perf_dic[key][TOTAL_STR]
        except Exception:
            tmp_dic = {}
        dic[target] = tmp_dic
    return dic

def get_detail_data( files, testItem, category ):
    dic = {}
    dic['sum'] = get_each_sum_item(files, testItem, category)
    for filename in files:
        with open(filename) as fp:
            data = json.load(fp)
        fp.close()
        try:
            perf_dic = data[RESULTS_STR][testItem][category]
            for key in perf_dic.keys():
                if (key != TOTAL_STR):
                    dic[key] = {}
            break
        except Exception:
            dic = {}
    for key in dic.keys():
        if (key == TOTAL_STR or key == 'sum'):
            continue
        tmp_dic = {}
        for filename in files:
            with open(filename) as fp:
                data = json.load(fp)
            fp.close()
            # get the target hostname from the filename
            target = '_'.join(filename.split('/')[-1].split('_')[:-2])
            test_points = data[RESULTS_STR][testItem][category][key]
            tmp_dic[target] = test_points[POINT_STR]
        dic[key] = tmp_dic
    return dic

def _deal_keyword(string):
    new_str = '_'.join(string.split('/'))
    new_str = '_'.join(new_str.split(' '))
    new_str = '_'.join(new_str.split('-'))
    return new_str

def index(request):
    show_picture.show_caliper_result()
    files = get_files()
    dic_total = {}
    dic_sum = get_sum_dics(files)
    dic_total['dic_sum'] = json.dumps(dic_sum)
    for key in dic_sum.keys():
        if dic_sum[key]:
            key = _deal_keyword(key)
            dic_total[key] = True
    return render(request, 'polls/index.html', dic_total)

def algorithm(request):
    files = get_files()
    dic_total = {}
    dic_alg = get_detail_data(files, PERF_STR, 'algorithm')
    dic_total['dic_alg'] = json.dumps(dic_alg)
    for key in dic_alg.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/algorithm.html', dic_total)

def cpu(request):
    files = get_files()
    dic_total = {}
    dic_cpu = get_detail_data(files, PERF_STR, 'cpu')
    dic_total['dic_cpu'] = json.dumps(dic_cpu)
    for key in dic_cpu.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/cpu.html', dic_total)

def disk(request):
    files = get_files()
    dic_total = {}
    dic_disk = get_detail_data(files, PERF_STR, 'disk')
    dic_total['dic_disk'] = json.dumps(dic_disk)
    for key in dic_disk.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/disk.html', dic_total)

def latency(request):
    files = get_files()
    dic_total = {}
    dic_lat = get_detail_data(files, PERF_STR, 'latency')
    dic_total['dic_lat'] = json.dumps(dic_lat)
    for key in dic_lat.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/latency.html', dic_total)

def memory(request):
    files = get_files()
    dic_total = {}
    dic_mem = get_detail_data(files, PERF_STR, 'memory')
    dic_total['dic_mem'] = json.dumps(dic_mem)
    for key in dic_mem.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/memory.html', dic_total)

def io(request):
    files = get_files()
    dic_total = {}
    dic_io = get_detail_data(files, PERF_STR, 'io')
    dic_total['dic_io'] = json.dumps(dic_io)
    for key in dic_io.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/io.html', dic_total)

def network(request):
    files = get_files()
    dic_total = {}
    dic_net = get_detail_data(files, PERF_STR, 'network')
    dic_total['dic_net'] = json.dumps(dic_net)
    for key in dic_net.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/network.html', dic_total)

def kernel(request):
    files = get_files()
    dic_total = {}
    dic_kernel = get_detail_data(files, FUNC_STR, 'kernel')
    dic_total['dic_kernel'] = json.dumps(dic_kernel)
    for key in dic_kernel.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/kernel.html', dic_total)

def debug(request):
    files = get_files()
    dic_total = {}
    dic_debug = get_detail_data(files, FUNC_STR, 'debug')
    dic_total['dic_debug'] = json.dumps(dic_debug)
    for key in dic_debug.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/debug.html', dic_total)

def peripheral(request):
    files = get_files()
    dic_total = {}
    dic_peripheral = get_detail_data(files, FUNC_STR, 'peripheral')
    dic_total['dic_peripheral'] = json.dumps(dic_peripheral)
    for key in dic_peripheral.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/peripheral.html', dic_total)

def application(request):
    files = get_files()
    dic_total = {}
    dic_application = get_detail_data(files, PERF_STR, 'application')
    dic_total['dic_application'] = json.dumps(dic_application)
    for key in dic_application.keys():
        key_name = _deal_keyword(key)
        dic_total[key_name] = True
    return render(request, 'polls/application.html', dic_total)


