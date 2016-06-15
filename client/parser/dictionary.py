import openpyxl
import copy
import sys
import yaml
import dictionary
import pdb
import glob
import os
import json
#from normalize import *
#from report import *
#from helper import *

def convertDic(oldDic):
    newDic = copy.deepcopy(oldDic)
    for top,category in oldDic.iteritems():
        if top == 'results':
            for category,sub_category in category.iteritems():
                for sub_category,scenario in sub_category.iteritems():
                    newDic[top][category][sub_category]['Total_Scores'] = 0
                    for scenario,key in scenario.iteritems():
                        del newDic[top][category][sub_category][scenario]
                        newDic[top][category][sub_category][scenario] = {}
                        newDic[top][category][sub_category][scenario]['Point_Scores'] = {}
                        newDic[top][category][sub_category][scenario]['Point_Scores'] = key
                        newDic[top][category][sub_category][scenario]['Point_Scores'] = key
                        newDic[top][category][sub_category][scenario]['Total_Scores'] = 0
    return newDic

def initialize_hw( test, dictionary ):
    i =  0
    for test_case in test:
        for category in test_case:
            if i == 0:
                top = category;
                if not dictionary.get(category):
                    dictionary[top] = {}
            elif i == 1:
                dimention = category
                if not dictionary[top].get(category):
                    dictionary[top][dimention] = {}
            elif i == 2:
                sub_category = category
                if not dictionary[top][dimention].get(category):
                    dictionary[top][dimention][sub_category] = {}
            i = i + 1
            i = i % 2
    return

def initailize( test, dictionary ):
    i =  0
    for test_case in test:
        for category in test_case:
            if i == 0:
                top = category;
                if not dictionary.get(category):
                    dictionary[top] = {}
            elif i == 1:
                dimention = category
                if not dictionary[top].get(category):
                    dictionary[top][dimention] = {}
            elif i == 2:
                sub_category = category
                if not dictionary[top][dimention].get(category):
                    dictionary[top][dimention][sub_category] = {}
            elif i == 3:
                scenario = category
                if not dictionary[top][dimention][sub_category].get(category):
                    dictionary[top][dimention][sub_category][scenario] = {}
            i = i + 1
            i = i % 4
    return

def cachebench(dic):
    c1 = ['results','Performance','memory','bandwidth']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['memory']['bandwidth']['cachebench_read'] = 0
    dic['results']['Performance']['memory']['bandwidth']['cachebench_rmw'] = 0
    dic['results']['Performance']['memory']['bandwidth']['cachebench_write'] = 0

def complie(dic):
    c1 = ['results','Performance','application','compile']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['application']['compile']['kernel-dev_1'] = 0
    dic['results']['Performance']['application']['compile']['kernel-dev_16'] = 0
    dic['results']['Performance']['application']['compile']['kernel-dev_2'] = 0
    dic['results']['Performance']['application']['compile']['kernel-dev_32'] = 0
    dic['results']['Performance']['application']['compile']['kernel-dev_4'] = 0
    dic['results']['Performance']['application']['compile']['kernel-dev_64'] = 0
    dic['results']['Performance']['application']['compile']['kernel-dev_72'] = 0
    dic['results']['Performance']['application']['compile']['kernel-dev_8'] = 0
    return

def coremark(dic):
    c1 = ['results','Performance','cpu','sincore_int']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['cpu']['sincore_int']['coremark'] = 0
    return

def dhrystone(dic):
    c1 = ['results','Performance','cpu','sincore_float']
    c2 = ['results','Performance','cpu','sincore_int']
    test = [ c1, c2 ]
    initailize(test , dic)
    dic['results']['Performance']['cpu']['sincore_int']['dhry1'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['dhry2'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['whets'] = 0
    return

def ebizzy(dic):
    c1 = ['results','Performance','application','ebizzy_M_r']
    c2 = ['results','Performance','application','ebizzy_m_r']
    c3 = ['results','Performance','application','ebizzy_m_t']
    c4 = ['results','Performance','application','ebizzy_M_t']
    test = [ c1, c2, c3, c4 ]
    initailize(test , dic)
    dic['results']['Performance']['application']['ebizzy_M_r']['records_1'] = 0
    dic['results']['Performance']['application']['ebizzy_M_r']['records_16'] = 0
    dic['results']['Performance']['application']['ebizzy_M_r']['records_2'] = 0
    dic['results']['Performance']['application']['ebizzy_M_r']['records_32'] = 0
    dic['results']['Performance']['application']['ebizzy_M_r']['records_4'] = 0
    dic['results']['Performance']['application']['ebizzy_M_r']['records_64'] = 0
    dic['results']['Performance']['application']['ebizzy_M_r']['records_8'] = 0
    dic['results']['Performance']['application']['ebizzy_M_r']['records_80'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_1'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_16'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_2'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_32'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_4'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_64'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_8'] = 0
    dic['results']['Performance']['application']['ebizzy_m_r']['records_80'] = 0
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_1'] = 0	
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_16'] = 0	
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_2'] = 0	
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_32'] = 0	
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_4'] = 0	
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_64'] = 0	
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_8'] = 0	
    dic['results']['Performance']['application']['ebizzy_M_t']['sys_80'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_1'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_16'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_2'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_32'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_4'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_64'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_8'] = 0	
    dic['results']['Performance']['application']['ebizzy_m_t']['sys_80'] = 0	
    return

def fio(dic):
    c1 = ['results','Performance','io','bandwidth']
    c2 = ['results','Performance','io','iops']
    test = [ c1,c2 ]
    initailize(test , dic)
    dic['results']['Performance']['io']['bandwidth']['fio_randread'] = 0
    dic['results']['Performance']['io']['bandwidth']['fio_randwrite'] = 0
    dic['results']['Performance']['io']['bandwidth']['fio_read'] = 0
    dic['results']['Performance']['io']['bandwidth']['fio_write'] = 0
    dic['results']['Performance']['io']['iops']['fio_randread'] = 0
    dic['results']['Performance']['io']['iops']['fio_randwrite'] = 0
    dic['results']['Performance']['io']['iops']['fio_read'] = 0
    dic['results']['Performance']['io']['iops']['fio_write'] = 0
    return

def hadoop(dic):
    c1 = ['results','Performance','application','hadoop']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['application']['hadoop']['HadoopBayes'] = 0
    dic['results']['Performance']['application']['hadoop']['HadoopDfsioe'] = 0
    dic['results']['Performance']['application']['hadoop']['HadoopKmeans'] = 0
    #dic['results']['Performance']['application']['hadoop']['HadoopSleep'] = 0
    dic['results']['Performance']['application']['hadoop']['HadoopSort'] = 0
    dic['results']['Performance']['application']['hadoop']['HadoopTerasort'] = 0
    dic['results']['Performance']['application']['hadoop']['HadoopWordcount'] = 0
    return

def iozone(dic):
    c1 = ['results','Performance','disk','Iozone-DirectIO']
    c2 = ['results','Performance','disk','Iozone-Cached']
    test = [ c1,c2 ]
    initailize(test , dic)
    dic['results']['Performance']['disk']['Iozone-DirectIO']['bkwd_read'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['fread'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['freread'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['frewrite'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['fwrite'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['random_read'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['random_write'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['read'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['recored_rewrite'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['reread'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['rewrite'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['stride_read'] = 0
    dic['results']['Performance']['disk']['Iozone-DirectIO']['write'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['bkwd_read'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['fread'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['freread'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['frewrite'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['fwrite'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['random_read'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['random_write'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['read'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['recored_rewrite'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['reread'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['rewrite'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['stride_read'] = 0
    dic['results']['Performance']['disk']['Iozone-Cached']['write'] = 0
    return

def iperf(dic):
    c1 = ['results','Performance','network','bandwidth']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['network']['bandwidth']['TCP_s1'] = 0
    dic['results']['Performance']['network']['bandwidth']['TCP_s3'] = 0
    dic['results']['Performance']['network']['bandwidth']['TCP_s5'] = 0
    dic['results']['Performance']['network']['bandwidth']['TCP_s10'] = 0
    return

def kselftest(dic):
#    c1 = ['results','Functional','kernel','cpu']
#    c2 = ['results','Functional','kernel','EFIFS']
#    c3 = ['results','Functional','kernel','memory']
#    c4 = ['results','Functional','kernel','posix']
#    c5 = ['results','Functional','kernel','network']
#    c6 = ['results','Functional','kernel','syscall']
#    c7 = ['results','Functional','kernel','vm']
#    test = [ c1,c2,c3,c4,c5,c6,c7 ]
#    initailize(test , dic)
#    dic['results']['Functional']['kernel']['cpu']['hotplog'] = 0
#    dic['results']['Functional']['kernel']['EFIFS']['efivarfs'] = 0
#    dic['results']['Functional']['kernel']['memory']['hotplog'] = 0
#    dic['results']['Functional']['kernel']['posix']['mqueue'] = 0
#    dic['results']['Functional']['kernel']['network']['sock'] = 0
#    dic['results']['Functional']['kernel']['syscall']['ptrace'] = 0
#    dic['results']['Functional']['kernel']['vm']['hugepage_mmap'] = 0
#    dic['results']['Functional']['kernel']['vm']['hugepage_shm'] = 0
#    dic['results']['Functional']['kernel']['vm']['hugetlb_map'] = 0
#    dic['results']['Functional']['kernel']['vm']['hugetlbfstest'] = 0
    return

def linpack(dic):
    c1 = ['results','Performance','cpu','sincore_float']
    c2 = ['results','Performance','cpu','sincore_double']
    test = [ c1,c2 ]
    initailize(test , dic)
    dic['results']['Performance']['cpu']['sincore_double']['linpack_dp'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['linpack_sp'] = 0
    return

def lmbench(dic):
    c1 = ['results','Performance','cpu','sincore_double']
    c2 = ['results','Performance','cpu','sincore_float']
    c3 = ['results','Performance','cpu','sincore_int']
    c4 = ['results','Performance','latency','ctx']
    c5 = ['results','Performance','latency','file/vm']
    c6 = ['results','Performance','latency','mem']
    c7 = ['results','Performance','latency','process']
    c8 = ['results','Performance','memory','local_speed']
    c9 = ['results','Performance','network','local_lat']
    test = [ c1,c2,c3,c4,c5,c6,c7,c8,c9 ]
    initailize(test , dic)
    dic['results']['Performance']['cpu']['sincore_double']['double_add'] = 0
    dic['results']['Performance']['cpu']['sincore_double']['double_bogomflops'] = 0
    dic['results']['Performance']['cpu']['sincore_double']['double_div'] = 0
    dic['results']['Performance']['cpu']['sincore_double']['double_mul'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['float_add'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['float_bogomflops'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['float_div'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['float_mul'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['integer_add'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['integer_bit'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['integer_div'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['integer_mod'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['integer_mul'] = 0
    dic['results']['Performance']['latency']['ctx']['16p/16K_ctxsw'] = 0
    dic['results']['Performance']['latency']['ctx']['16p/64K_ctxsw'] = 0
    dic['results']['Performance']['latency']['ctx']['2p/0K_ctxsw'] = 0
    dic['results']['Performance']['latency']['ctx']['2p/16K_ctxsw'] = 0
    dic['results']['Performance']['latency']['ctx']['2p/64K_ctxsw'] = 0
    dic['results']['Performance']['latency']['ctx']['8p/16K_ctxsw'] = 0
    dic['results']['Performance']['latency']['ctx']['8p/64K_ctxsw'] = 0
    dic['results']['Performance']['latency']['file/vm']['0k_file_create'] = 0
    dic['results']['Performance']['latency']['file/vm']['0k_file_delete'] = 0
    dic['results']['Performance']['latency']['file/vm']['100fd_select'] = 0
    dic['results']['Performance']['latency']['file/vm']['10k_file_create'] = 0
    dic['results']['Performance']['latency']['file/vm']['10k_file_delete'] = 0
    dic['results']['Performance']['latency']['file/vm']['Mmap(KB)'] = 0
#    dic['results']['Performance']['latency']['file/vm']['Page_fault'] = 0
    dic['results']['Performance']['latency']['file/vm']['Prot_fault'] = 0
    dic['results']['Performance']['latency']['mem']['L1'] = 0
    dic['results']['Performance']['latency']['mem']['L2'] = 0
    dic['results']['Performance']['latency']['mem']['Main_memory'] = 0
    dic['results']['Performance']['latency']['process']['exec_proc'] = 0
    dic['results']['Performance']['latency']['process']['fork_proc'] = 0
    dic['results']['Performance']['latency']['process']['null_IO'] = 0
    dic['results']['Performance']['latency']['process']['null_call'] = 0
    dic['results']['Performance']['latency']['process']['open_close'] = 0
    dic['results']['Performance']['latency']['process']['sh_proc'] = 0
    dic['results']['Performance']['latency']['process']['sig_hndl'] = 0
    dic['results']['Performance']['latency']['process']['sig_inst'] = 0
    dic['results']['Performance']['latency']['process']['slct_TCP'] = 0
    dic['results']['Performance']['latency']['process']['stat'] = 0
    dic['results']['Performance']['network']['local_lat']['AF_Unix'] = 0
    dic['results']['Performance']['network']['local_lat']['Pipe'] = 0
    dic['results']['Performance']['network']['local_lat']['TCP'] = 0
    dic['results']['Performance']['network']['local_lat']['TCP_con'] = 0
    dic['results']['Performance']['network']['local_lat']['UDP'] = 0
    dic['results']['Performance']['memory']['local_speed']['AF_Unix'] = 0
    dic['results']['Performance']['memory']['local_speed']['BCopy(hand_partial)'] = 0
    dic['results']['Performance']['memory']['local_speed']['Bcopy(hand)'] = 0
    dic['results']['Performance']['memory']['local_speed']['Bcopy(libc)'] = 0
    dic['results']['Performance']['memory']['local_speed']['Bcopy(libc_a)'] = 0
    dic['results']['Performance']['memory']['local_speed']['Bzero'] = 0
    dic['results']['Performance']['memory']['local_speed']['File_reread'] = 0
    dic['results']['Performance']['memory']['local_speed']['Mem_RW_partial'] = 0
    dic['results']['Performance']['memory']['local_speed']['Mem_read'] = 0
    dic['results']['Performance']['memory']['local_speed']['Mem_read_partial'] = 0
    dic['results']['Performance']['memory']['local_speed']['Mem_write'] = 0
    dic['results']['Performance']['memory']['local_speed']['Mem_write_partial'] = 0
    dic['results']['Performance']['memory']['local_speed']['Mmap_open2close'] = 0
    dic['results']['Performance']['memory']['local_speed']['Mmap_reread'] = 0
    dic['results']['Performance']['memory']['local_speed']['Pipe'] = 0
    dic['results']['Performance']['memory']['local_speed']['Reread_open2close'] = 0
    dic['results']['Performance']['memory']['local_speed']['TCP'] = 0
    return

def ltp(dic):
    c1 = ['results','Functional','kernel','cpu']
    c2 = ['results','Functional','kernel','dio']
    c3 = ['results','Functional','kernel','fs']
    c4 = ['results','Functional','kernel','kernel']
    c5 = ['results','Functional','kernel','memory']
    c6 = ['results','Functional','kernel','proc']
    test = [ c1,c2,c3,c4,c5,c6 ]
    initailize(test , dic)
    dic['results']['Functional']['kernel']['cpu']['ltp'] = 0
    dic['results']['Functional']['kernel']['dio']['ltp'] = 0
    dic['results']['Functional']['kernel']['fs']['ltp'] = 0
    dic['results']['Functional']['kernel']['kernel']['ltp'] = 0
    dic['results']['Functional']['kernel']['memory']['ltp'] = 0
    dic['results']['Functional']['kernel']['proc']['ltp'] = 0
    return

def memtester(dic):
#    c1 = ['results','Functional','peripheral','memory']
#    test = [ c1 ]
#    initailize(test , dic)
#    dic['results']['Functional']['peripheral']['memory']['memtester'] = 0
    return

def nbench(dic):
    c1 = ['results','Performance','cpu','sincore_float']
    c2 = ['results','Performance','cpu','sincore_int']
    test = [ c1,c2 ]
    initailize(test , dic)
    dic['results']['Performance']['cpu']['sincore_float']['FOURIER'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['LU DECOMPOSITION'] = 0
    dic['results']['Performance']['cpu']['sincore_float']['NEURAL NET'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['ASSIGNMENT'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['BITFIELD'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['FP EMULATION'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['HUFFMAN'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['IDEA'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['NUMERIC SORT'] = 0
    dic['results']['Performance']['cpu']['sincore_int']['STRING SORT'] = 0
    return

def netperf(dic):
    c1 = ['results','Performance','network','bandwidth']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['network']['bandwidth']['TCP_CRR'] = 0
    dic['results']['Performance']['network']['bandwidth']['TCP_RR'] = 0
    dic['results']['Performance']['network']['bandwidth']['TCP_stream'] = 0
    dic['results']['Performance']['network']['bandwidth']['TCP_stream_r'] = 0
    dic['results']['Performance']['network']['bandwidth']['UDP_RR'] = 0
    return

def openssl(dic):
    c1 = ['results','Performance','algorithm','digital sign']
    c2 = ['results','Performance','algorithm','digital verify']
    c3 = ['results','Performance','algorithm','hash algorithm']
    c4 = ['results','Performance','algorithm','symmetric cyphers']
    test = [ c1,c2,c3,c4 ]
    initailize(test , dic)
    dic['results']['Performance']['algorithm']['digital sign']['dsa'] = 0
    dic['results']['Performance']['algorithm']['digital sign']['ecdsa'] = 0
    dic['results']['Performance']['algorithm']['digital sign']['rsa'] = 0
    dic['results']['Performance']['algorithm']['digital verify']['dsa'] = 0
    dic['results']['Performance']['algorithm']['digital verify']['ecdsa'] = 0
    dic['results']['Performance']['algorithm']['digital verify']['rsa'] = 0
    dic['results']['Performance']['algorithm']['hash algorithm']['md5'] = 0
    dic['results']['Performance']['algorithm']['hash algorithm']['sha1'] = 0
    dic['results']['Performance']['algorithm']['hash algorithm']['sha256'] = 0
    dic['results']['Performance']['algorithm']['hash algorithm']['sha512'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['aes-128 cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['aes-128 ige'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['aes-192 cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['aes-192 ige'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['aes-256 cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['aes-256 ige'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['blowfish cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['cast cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['des cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['des ede3'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['idea cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['rc2 cbc'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['rc4'] = 0
    dic['results']['Performance']['algorithm']['symmetric cyphers']['seed cbc'] = 0
    return

def perf(dic):
    c1 = ['results','Functional','debug','perf']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Functional']['debug']['perf']['record'] = 0
    dic['results']['Functional']['debug']['perf']['report'] = 0
    dic['results']['Functional']['debug']['perf']['stat'] = 0
    dic['results']['Functional']['debug']['perf']['test'] = 0
    return

def rttest(dic):
    c1=['results','Performance','latency','rttest']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['latency']['rttest']['cyclictest'] = 0
    dic['results']['Performance']['latency']['rttest']['hackbench_process'] = 0
    dic['results']['Performance']['latency']['rttest']['hackbench_thread'] = 0
#    dic['results']['Performance']['latency']['rttest']['pi-stress'] = 0
    dic['results']['Performance']['latency']['rttest']['pmqtest'] = 0
    dic['results']['Performance']['latency']['rttest']['ptsematest'] = 0
    dic['results']['Performance']['latency']['rttest']['rt-migrate-test'] = 0
    dic['results']['Performance']['latency']['rttest']['signaltest'] = 0
    dic['results']['Performance']['latency']['rttest']['sigwaittest'] = 0
    dic['results']['Performance']['latency']['rttest']['svsematest'] = 0
    return

def scimark(dic):
    c1=['results','Performance','cpu','sincore_float']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['cpu']['sincore_float']['scimark'] = 0
    return

def scimarkJava(dic):
    c1=['results','Performance','application','jdk']	
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['application']['jdk']['scimark'] = 0
    return

def sysbench(dic):
    c1=['results','Performance','application','sysbench'] 
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['application']['sysbench']['avg'] = 0 
    dic['results']['Performance']['application']['sysbench']['max'] = 0 
    dic['results']['Performance']['application']['sysbench']['min'] = 0 
    dic['results']['Performance']['application']['sysbench']['percentile'] = 0 
    return

def tinymembench(dic):
    c1=['results','Performance','memory','tiny_bandwidth']
    c2=['results','Performance','memory','tiny_latency']
    test = [ c1,c2 ]
    initailize(test , dic)
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_2-pass_copy'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_2-pass_copy_prefetched_32B'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_2-pass_copy_prefetched_64B'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_copy'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_copy_backwards'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_copy_prefetched_32B'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_copy_prefetched_64B'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['C_fill'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['standard_memcpy'] = 0
    dic['results']['Performance']['memory']['tiny_bandwidth']['standard_memset'] = 0
    dic['results']['Performance']['memory']['tiny_latency']['Hugepage_dual_random_read'] = 0
    dic['results']['Performance']['memory']['tiny_latency']['Hugepage_single_random_read'] = 0
    dic['results']['Performance']['memory']['tiny_latency']['No_Hugepage_dual_random_read'] = 0
    dic['results']['Performance']['memory']['tiny_latency']['No_Hugepage_single_random_read'] = 0
    return

def unzip(dic):
    c1=['results','Performance','application','unzip']
    test = [ c1 ]
    initailize(test , dic)
    dic['results']['Performance']['application']['unzip']['tar'] = 0
    return

def cpu(dic):
    c1=['Hardware_Info','CPU']
    test = [ c1 ] 
    initialize_hw(test , dic)
    dic['Hardware_Info']['CPU']['Model_Name'] = 0
    dic['Hardware_Info']['CPU']['Architecture'] = 0
    dic['Hardware_Info']['CPU']['Sockets'] = 0
    dic['Hardware_Info']['CPU']['Cores_Per_Socket'] = 0
    dic['Hardware_Info']['CPU']['Threads_per_Core'] = 0
    dic['Hardware_Info']['CPU']['CPU_Cores'] = 0
    dic['Hardware_Info']['CPU']['Numa_Node'] = 0
    dic['Hardware_Info']['CPU']['BogoMIPS'] = 0
    dic['Hardware_Info']['CPU']['Byte_Order'] = 0
    dic['Hardware_Info']['CPU']['Cpu_Type'] = 0
    return

def disk(dic):
    c1=['Hardware_Info','DISK']
    test = [ c1 ]
    initialize_hw(test , dic)
    dic['Hardware_Info']['DISK']['RAID_Card'] = 0
    dic['Hardware_Info']['DISK']['sda_Size'] = 0
    dic['Hardware_Info']['DISK']['sda_Serial'] = 0
    dic['Hardware_Info']['DISK']['sda_Model'] = 0
    dic['Hardware_Info']['DISK']['sda_Vendor'] = 0
    dic['Hardware_Info']['DISK']['sdb_Size'] = 0
    dic['Hardware_Info']['DISK']['sdb_Serial'] = 0
    dic['Hardware_Info']['DISK']['sdb_Model'] = 0
    dic['Hardware_Info']['DISK']['sdb_Vendor'] = 0
    dic['Hardware_Info']['DISK']['RAID_Vendor'] = 0
    return

def network(dic):
    c1=['Hardware_Info','NETWORK']
    test = [ c1 ]
    initialize_hw(test , dic)
    dic['Hardware_Info']['NETWORK']['PCI_Gigabit_Card'] = [] 
    return

def memory(dic):
    c1=['Hardware_Info','MEMORY']
    test = [ c1 ]
    initialize_hw(test , dic)
    dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size'] = 0
    dic['Hardware_Info']['MEMORY']['L1_D-Cache_Associativity'] = 0
    dic['Hardware_Info']['MEMORY']['L1_D-Cache_Operational_Mode'] = 0
    dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size'] = 0
    dic['Hardware_Info']['MEMORY']['L1_I-Cache_Associativity'] = 0
    dic['Hardware_Info']['MEMORY']['L1_I-Cache_Operational_Mode'] = 0
    dic['Hardware_Info']['MEMORY']['L2_Cache_Size'] = 0
    dic['Hardware_Info']['MEMORY']['L2_Cache_Associativity'] = 0
    dic['Hardware_Info']['MEMORY']['L2_Cache_Operational_Mode'] = 0
    dic['Hardware_Info']['MEMORY']['L3_Cache_Size'] = 0
    dic['Hardware_Info']['MEMORY']['L3_Cache_Associativity'] = 0
    dic['Hardware_Info']['MEMORY']['L3_Cache_Operational_Mode'] = 0
    dic['Hardware_Info']['MEMORY']['Main_Memory_Type'] = 0
    dic['Hardware_Info']['MEMORY']['Main_Memory_Formfactor'] = 0
    dic['Hardware_Info']['MEMORY']['Main_Memory_Max_Speed'] = 0
    dic['Hardware_Info']['MEMORY']['Main_Memory_Current_Speed'] = 0
    dic['Hardware_Info']['MEMORY']['Main_Memory_Manufacturer'] = 0
    dic['Hardware_Info']['MEMORY']['Main_Memory_Part_number'] = 0
    dic['Hardware_Info']['MEMORY']['Main_Memory_Size'] = 0
    return

def kernel(dic):
    c1=['Hardware_Info','KERNEL']
    test = [ c1 ]
    initialize_hw(test , dic)
    dic['Hardware_Info']['KERNEL']['Version'] = 0
    return

def os(dic):
    c1=['Hardware_Info','OS']
    test = [ c1 ]
    initialize_hw(test , dic)
    dic['Hardware_Info']['OS']['Distributor_ID'] = 0
    dic['Hardware_Info']['OS']['Description'] = 0
    dic['Hardware_Info']['OS']['Release'] = 0
    dic['Hardware_Info']['OS']['Codename'] = 0
    dic['Hardware_Info']['OS']['GCC_Version'] = 0
    dic['Hardware_Info']['OS']['LD_Version'] = 0
    return

