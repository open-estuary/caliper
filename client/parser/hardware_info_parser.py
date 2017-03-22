#!/usr/bin/python
import yaml
import logging
import dictionary
import glob
import os
import re
import pdb
import subprocess
import time
import caliper.server.utils as server_utils
from caliper.server.hosts import host_factory
from caliper.client.shared import error
from caliper.client.shared.settings import settings
from caliper.client.shared.caliper_path import folder_ope as Folder
path = "./HardwareInfo"
out_path = "./hardware_yaml"
lscpu_list = ['Architecture','Socket\(s\)','Cpu_Type','Core\(s\) per socket','Thread\(s\) per core','Model name','CPU\(s\)','NUMA node\(s\)','BogoMIPS','Byte Order']
lsb_release_list = ['Distributor ID','Description','Release','Codename']
lspci_list = ['Ethernet controller [0200]']
def get_remote_host():
    try:
        client_ip = settings.get_value('TARGET', 'ip', type=str)
    except Exception, e:
        client_ip = '127.0.0.1'
    try:
        port = settings.get_value('TARGET', 'port', type=int)
    except Exception, e:
        port = 22
    try:
        user = settings.get_value('TARGET', 'user', type=str)
    except Exception, e:
        user = os.getlogin()
    try:
        password = settings.get_value('TARGET', 'password', type=str)
    except Exception, e:
        raise error.ServRunError(e.args[0], e.args[1])

    remote_host = host_factory.create_host(client_ip, user, password, port)
    return remote_host

def network_populate(dic,contents):
    bogo = 0
    for blocks in contents:
        if blocks != '':
          if re.search(r'(\d+)[.]([\w /]+)', blocks):
            group = re.search(r'(\d+)[.]([\w /]+)', blocks)
            if group.group(2).strip() == "lspci":
                lspci_list.sort()
                key_lists = dic['Hardware_Info']['NETWORK'].keys()
                key_lists.sort()
                pci_info = []
                for i in range(0,(len(key_lists))):
                    pci_details = "*TBA"
                    if bool(re.search(r'Ethernet controller \[0200\]:\s+([\w\S ]+)',blocks)):
                        group_keys = re.findall(r'Ethernet controller \[0200\]:\s+([\w\S ]+)',blocks)
                        for group_key in group_keys:
                            pci_detail = " ".join(map(str,group_key.split(' ' )[0:-3]))
                            if pci_detail not in pci_info:
                                pci_info.append(pci_detail)
                        pci_infoas = ",".join(map(str,pci_info))

                    try:
                        dic['Hardware_Info']['NETWORK'][key_lists[i]] = pci_infoas
                    except:
                        dic['Hardware_Info']['NETWORK'][key_lists[i]] = "*TBA"
                continue
    return

def os_populate(dic,contents):
    for blocks in contents:
        if blocks != '':
          if re.search(r'(\d+)[.]([\w /]+)', blocks):
            group = re.search(r'(\d+)[.]([\w /]+)', blocks)
            if group.group(2).strip() == "lsb_release":
                lsb_release_list.sort()
                key_lists = dic['Hardware_Info']['OS'].keys()
                key_lists.remove('GCC_Version')
                key_lists.remove('LD_Version')
                key_lists.sort()
                for i in range(0,len(lsb_release_list)):
                    command = str(lsb_release_list[i]) + ':' +"\s+([\w\S ]+)"
                    if re.search(command,blocks):
                        group_keys = re.search(command,blocks)
                        try:
                            dic['Hardware_Info']['OS'][key_lists[i]] = group_keys.group(1)
                        except:
                            dic['Hardware_Info']['OS'][key_lists[i]] = "*TBA"
            elif group.group(2).strip() == "gcc":
               item = re.search(r'(\d+\.\d+\.\d+)\n',blocks)
               dic['Hardware_Info']['OS']['GCC_Version'] = item.group(1)
            elif group.group(2).strip() == "ld":
               item = re.search(r'(\d+\.\d+)\n',blocks)
               dic['Hardware_Info']['OS']['LD_Version'] = item.group(1)
    return

def cpu_populate(dic,contents):
    bogo = 0
    for blocks in contents:
        if blocks != '':
          if re.search(r'(\d+)[.]([\w /]+)', blocks):
            group = re.search(r'(\d+)[.]([\w /]+)', blocks)
            if group.group(2) == "lscpu":
                lscpu_list.sort()
                key_lists = dic['Hardware_Info']['CPU'].keys()
                key_lists.sort()
                for i in range(0,len(lscpu_list)):
                    command =  str(lscpu_list[i]) + ':' +"\s+([\w\S ]+)"
                    if bool(re.search(command,blocks,re.I)):
                        group_keys = re.search(command,blocks,re.I)
                        if lscpu_list[i] != 'BogoMIPS' or bogo == 0:
                            try:
                                dic['Hardware_Info']['CPU'][key_lists[i]] = group_keys.group(1)
                            except:
                                dic['Hardware_Info']['CPU'][key_lists[i]] = "*TBA"
            elif re.search("cat /proc/cpuinfo",blocks):
                if bool(re.search(r'\s+BogoMIPS\s+:\s+([\w\S ]+)',blocks)):
                    asd = re.search(r'\s+BogoMIPS\s+:\s+([\w\S ]+)',blocks,re.I)
                    dic['Hardware_Info']['CPU']['BogoMIPS'] = asd.group(1).strip()
                    bogo = bogo+1
                if bool(re.search(r'\s*model name\s+:\s+([\w\S ])+',blocks)):
                    asd = re.search(r'\s*model name\s+:\s+([\w\S ]+)',blocks,re.I)
                    dic['Hardware_Info']['CPU']['Cpu_Type'] = asd.group(1).strip()

    return

def kernel_populate(dic,contents):
    for blocks in contents:
        if blocks != '':
          if re.search(r'(\d+)[.]([\w /]+)', blocks):
            group = re.search(r'(\d+)[.]([\w /]+)', blocks)
            if group.group(2).strip() == "uname":
                key_lists = dic['Hardware_Info']['KERNEL'].keys()
                key_lists.sort()
                for i in range(0,len(key_lists)):
                    blocks = blocks.splitlines()
                    output = "Linux " + blocks[3].split(' ')[2]
                    try:
                        dic['Hardware_Info']['KERNEL'][key_lists[i]] = output
                    except:
                        dic['Hardware_Info']['KERNEL'][key_lists[i]] = "*TBA"
    return
    

def disk_populate(dic,contents):
    for blocks in contents:
        if blocks != '':
          if re.search(r'(\d+)[.]([\w /]+)', blocks):
            group = re.search(r'(\d+)[.]([\w /]+)', blocks)
            if group.group(2).strip() == "lshw":
                block = blocks.split("     *-scsi")
                if len(block)>1:
                    items = block[1].split("        *-disk")
                    if len(items)>1:
                        if bool(re.search(r'\s+product:\s([\w\S ]+)',items[1])):
                            asd = re.search(r'\s+product:\s([\w\S ]+)',items[1])
                            dic['Hardware_Info']['DISK']['sda_Model']= asd.group(1).strip()
                        if bool(re.search(r'\s+vendor:\s([\w\S ]+)',items[1])):
                            asd = re.search(r'\s+vendor:\s([\w\S ]+)',items[1])
                            dic['Hardware_Info']['DISK']['sda_Vendor']= asd.group(1).strip()
                        if bool(re.search(r'\s+size:\s([\w\S ]+)',items[1])):
                            asd = re.search(r'\s+size:\s([\w\S ]+)',items[1])
                            dic['Hardware_Info']['DISK']['sda_Size']= asd.group(1).strip()
                        if bool(re.search(r'\s+serial:\s([\w\S ]+)',items[1])):
                            asd = re.search(r'\s+serial:\s([\w\S ]+)',items[1])
                            dic['Hardware_Info']['DISK']['sda_Serial']= asd.group(1).strip()
                    if len(items)>2:
                        if bool(re.search(r'\s+product:\s([\w\S ]+)',items[2])):
                            asd = re.search(r'\s+product:\s([\w\S ]+)',items[2])
                            dic['Hardware_Info']['DISK']['sdb_Model']= asd.group(1).strip()
                        if bool(re.search(r'\s+vendor:\s([\w\S ]+)',items[2])):
                            asd = re.search(r'\s+vendor:\s([\w\S ]+)',items[2])
                            dic['Hardware_Info']['DISK']['sdb_Vendor']= asd.group(1).strip()
                        if bool(re.search(r'\s+size:\s([\w\S ]+)',items[2])):
                            asd = re.search(r'\s+size:\s([\w\S ]+)',items[2])
                            dic['Hardware_Info']['DISK']['sdb_Size']= asd.group(1).strip()
                        if bool(re.search(r'\s+serial:\s([\w\S ]+)',items[2])):
                            asd = re.search(r'\s+serial:\s([\w\S ]+)',items[2])
                            dic['Hardware_Info']['DISK']['sdb_Serial']= asd.group(1).strip()
                block = blocks.split("           *-storage")
                if len(block)>1:
                    if bool(re.search(r'description: RAID',block[1])):
                        if bool(re.search(r'\s+product:\s([\w\S ]+)',block[1])):
                            asd = re.search(r'\s+product:\s([\w\S ]+)',block[1])
                            dic['Hardware_Info']['DISK']['RAID_Card']= asd.group(1).strip()
                        if bool(re.search(r'\s+vendor:\s([\w\S ]+)',block[1])):
                            asd = re.search(r'\s+vendor:\s([\w\S ]+)',block[1])
                            dic['Hardware_Info']['DISK']['RAID_Vendor']= asd.group(1).strip()
            elif group.group(2).strip() == "lsblk":
                #if bool(re.search(r'sda\s+([\d.]+G)[\w\S ]+',blocks)):
                    #asd = re.search(r'sda\s+([\d.]+G)[\w\S ]+',blocks)
                if bool(re.search(r'sdb\s+[\w\s]+\s+([\d\.]+G)\s+([\w]+)[\w\s]+disk\s+([A-Za-z]+)',blocks)):
                    asd = re.search(r'sdb\s+[\w\s]+\s+([\d\.]+G)\s+([\w]+)[\w\s]+disk\s+([A-Za-z]+)',blocks)
                    dic['Hardware_Info']['DISK']['sdb_Size']= asd.group(1).strip()
                    dic['Hardware_Info']['DISK']['sdb_Model']= asd.group(2).strip()
                    dic['Hardware_Info']['DISK']['sdb_Vendor']= asd.group(3).strip()
                if bool(re.search(r'sda\s+[\w\s]+\s+([\d\.]+G)\s+([\w]+)[\w\s]+disk\s+([A-Za-z]+)',blocks)):
                    asd = re.search(r'sda\s+[\w\s]+\s+([\d\.]+G)\s+([\w]+)[\w\s]+disk\s+([A-Za-z]+)',blocks)
                    dic['Hardware_Info']['DISK']['sda_Size']= asd.group(1).strip()
                    dic['Hardware_Info']['DISK']['sda_Model']= asd.group(2).strip()
                    dic['Hardware_Info']['DISK']['sda_Vendor']= asd.group(3).strip()
                #if bool(re.search(r'sdb\s+ext4\s+([\d\.]+G)[\w\S ]+',blocks)):
                #    asd = re.search(r'sdb\s+ext4\s+([\d\.]+G)[\w\S ]+',blocks)
                #    dic['Hardware_Info']['DISK']['sdb_Size']= asd.group(1).strip()
    return


    
def memory_populate(dic,contents):
    flag = [0,0,0,0]
    for blocks in contents:
        if blocks != '':
          if re.search(r'(\d+)[.]([\w /]+)', blocks):
            group = re.search(r'(\d+)[.]([\w /]+)', blocks)
            if group.group(2).strip() == "dmidecode":
                block = blocks.split('\n\n')
                main_mem = ['Form Factor','Type','Speed','Manufacturer','Part Number','Configured Clock Speed']
                main_mem_key = ['Main_Memory_Formfactor','Main_Memory_Type','Main_Memory_Max_Speed','Main_Memory_Manufacturer','Main_Memory_Part_number','Main_Memory_Current_Speed']
                i = 0
                for item in block:
                    if bool(re.search(r'Memory Device\n',item)):
                        i = i + 1
                        if i < 2 :
                            continue
                        if i > 3 :
                            break
                        for i in range(0,len(main_mem)):
                            command = "\s+" +  str(main_mem[i]) + ':' +"\s([\w\S ]+)"
                            if bool(re.search(command,item,re.I)):
                                group_keys = re.search(command,item,re.I)
                                try:
                                    dic['Hardware_Info']['MEMORY'][main_mem_key[i]] = group_keys.group(1)
                                except:
                                    dic['Hardware_Info']['MEMORY'][main_mem_key[i]] = "*TBA"
                                   
                            
                for item in block:
                    if bool(re.search(r'Cache Information\n',item)):
                            for i in [2,3]:
                                command = "Level " + str(i)
                                if bool(re.search(command,item)):
                                    key = "L" + str(i) + "_Cache_Operational_Mode"
                                    if bool(re.search(r'\s+Operational Mode:\s([\w\S ]+)',item)):
                                        asd = re.search(r'\s+Operational Mode:\s([\w\S ]+)',item)
                                        dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    else:
                                       dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    key = "L" + str(i) + "_Cache_Associativity"
                                    if bool(re.search(r'\s+Associativity:\s([\w\S ]+)',item)):
                                       asd = re.search(r'\s+Associativity:\s([\w\S ]+)',item)
                                       dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    key = "L" + str(i) + "_Cache_Size"
                                    if flag[i] != 1:
                                       if bool(re.search(r'\s+Installed Size:\s([\w\S ]+)',item)):

                                           asd = re.search(r'\s+Installed Size:\s([\w\S ]+)',item)
                                           dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                            if bool(re.search('Level 1',item)) and (bool(re.search('Instruction',item)) or bool(re.search('Unified',item))):
                                    key = "L1_I-Cache_Operational_Mode"
                                    if bool(re.search(r'\s+Operational Mode:\s([\w\S ]+)',item)):
                                        asd = re.search(r'\s+Operational Mode:\s([\w\S ]+)',item)
                                        dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    else:
                                       dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    key = "L1_I-Cache_Associativity"
                                    if bool(re.search(r'\s+Associativity:\s([\w\S ]+)',item)):
                                       asd = re.search(r'\s+Associativity:\s([\w\S ]+)',item)
                                       dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    key = "L1_I-Cache_Size"
                                    if flag[1] != 1:
                                       if bool(re.search(r'\s+Installed Size:\s([\w\S ]+)',item)):
                                           asd = re.search(r'\s+Installed Size:\s([\w\S ]+)',item)
                                           dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                            elif bool(re.search('Level 1',item)) and (bool(re.search('Data',item)) or bool(re.search('Unified',item))):
                                    key = "L1_D-Cache_Operational_Mode"
                                    if bool(re.search(r'\s+Operational Mode:\s([\w\S ]+)',item)):
                                        asd = re.search(r'\s+Operational Mode:\s([\w\S ]+)',item)
                                        dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    else:
                                       dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    key = "L1_D-Cache_Associativity"
                                    if bool(re.search(r'\s+Associativity:\s([\w\S ]+)',item)):
                                       asd = re.search(r'\s+Associativity:\s([\w\S ]+)',item)
                                       dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
                                    key = "L1_D-Cache_Size"
                                    if flag[0] != 1:
                                       if bool(re.search(r'\s+Installed Size:\s([\w\S ]+)',item)):
                                           asd = re.search(r'\s+Installed Size:\s([\w\S ]+)',item)
                                           dic['Hardware_Info']['MEMORY'][key] = asd.group(1).strip()
            elif group.group(2) == "lscpu":
                lscpu_mem = ['L1d cache','L1i cache','L2 cache','L3 cache']
                key_lists = ['L1_D-Cache_Size','L1_I-Cache_Size','L2_Cache_Size','L3_Cache_Size']
                for i in range(0,len(lscpu_mem)):
                    command = "\s+" +  str(lscpu_mem[i]) + ':' +"\s+([\w\S ]+)"
                    if bool(re.search(command,blocks,re.I)):
                        group_keys = re.search(command,blocks,re.I)
                        try:
                            dic['Hardware_Info']['MEMORY'][key_lists[i]] = group_keys.group(1)
                        except:
                            dic['Hardware_Info']['MEMORY'][key_lists[i]] = "*TBA"
            elif re.search(r'free',group.group(2)):
               item = re.search(r'(\d+)',blocks.splitlines()[-1])
               dic['Hardware_Info']['MEMORY']['Main_Memory_Size'] = item.group(1) + "MB"

    return 

    

def update(dic,outfp):
    update_list = ['Unknown','Not specified',0,'[]','']
    for hardware_info,category_dic in dic.iteritems():
        for category,info_dic in category_dic.iteritems():
            for key,value in info_dic.iteritems():
                if value in update_list:
                    dic[hardware_info][category][key] = "*TBA"
    #files = ['./HardwareInfo/D02-32G_Targetinfo']
    #if filename in files:
    #    cores = int(dic['Hardware_Info']['CPU']['CPU_Cores'])
    #    cached = int(dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size'].split(' ')[0])
    #    cachei = int(dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size'].split(' ')[0])
    #    cached = str(cached/cores) + ' kB'
    #    cachei = str(cachei/cores) + ' kB'

    #    dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size'] = cached
    #    dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size'] = cachei

    outfp.write(yaml.dump(dic,default_flow_style=False))
    return 


def hardware_info_parser(content,outfp):
    category = {
        '[CPU]' : dictionary.cpu,
        '[DISK]' : dictionary.disk,
        '[NETWORK]' : dictionary.network,
        '[MEMORY]' : dictionary.memory,
        '[KERNEL]' : dictionary.kernel,
        '[OS]' : dictionary.os
    }
    dic = {}
    dic_yaml = {}
    dic_yaml['Configuration'] = {}
    dic_yaml['name'] = {}
    contents = content.split('\n\n\n')
    for key,value in category.iteritems():
        value(dic)
    try:
    	os_populate(dic,contents)
    except Exception as e:
	pass
    try:
    	cpu_populate(dic,contents)
    except Exception as e:
	pass
    try:
    	memory_populate(dic,contents)
    except Exception as e:
	pass
    try:
    	disk_populate(dic,contents)
    except Exception as e:
	pass
    try:
    	kernel_populate(dic,contents)
    except Exception as e:
	pass
    try:
    	network_populate(dic,contents)
    except Exception as e:
	pass
    update(dic,outfp)
    host = get_remote_host()
    dic_yaml['Configuration']['CPU'] = dic['Hardware_Info']['CPU']['CPU_Cores']
    dic_yaml['Configuration']['CPU_type'] = dic['Hardware_Info']['CPU']['Cpu_Type']
    dic_yaml['Configuration']['Memory'] = dic['Hardware_Info']['MEMORY']['Main_Memory_Size']
    dic_yaml['Configuration']['OS_Version'] = dic['Hardware_Info']['KERNEL']['Version']
    dic_yaml['Configuration']['Byte_order'] = dic['Hardware_Info']['CPU']['Byte_Order']
    dic_yaml['Configuration']['Hostname'] = server_utils.get_host_name(host)
    dic_yaml['Configuration']['L1d_cache'] = dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size']
    dic_yaml['Configuration']['L1i_cache'] = dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size']
    dic_yaml['Configuration']['L2_cache'] = dic['Hardware_Info']['MEMORY']['L2_Cache_Size']
    dic_yaml['Configuration']['L3_cache'] = dic['Hardware_Info']['MEMORY']['L3_Cache_Size']
    dic_yaml['Configuration']['Machine_arch'] = dic['Hardware_Info']['CPU']['Architecture']
    dic_yaml['name'] = dic_yaml['Configuration']['Hostname']
    yaml_name = dic_yaml['Configuration']['Hostname'] + ".yaml"
    yaml_path = os.path.join(Folder.yaml_dir,yaml_name)
    with open(yaml_path,'w') as outfp:
        outfp.write(yaml.dump(dic_yaml,default_flow_style = False))
    yaml_name_hw = dic_yaml['Configuration']['Hostname'] + "_hw_info.yaml"
    yaml_path_hw = os.path.join(Folder.yaml_dir,yaml_name_hw)
    with open(yaml_path_hw,'w') as outfp:
        outfp.write(yaml.dump(dic,default_flow_style = False))
    return dic
