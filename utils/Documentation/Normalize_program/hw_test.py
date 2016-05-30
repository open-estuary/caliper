#!/usr/bin/python
import yaml
import dictionary
import glob
import os
import re
import pdb
import time

out_path = "./hardware_yaml"
lscpu_list = ['Architecture','Socket\(s\)','Core\(s\) per socket','Thread\(s\) per core','Model name','CPU\(s\)','NUMA node\(s\)','BogoMIPS']
lsb_release_list = ['Distributor ID','Description','Release','Codename']
lspci_list = ['Ethernet controller [0200]']

category = {
    '[CPU]': dictionary.cpu,
    '[DISK]': dictionary.disk,
    '[NETWORK]': dictionary.network,
    '[MEMORY]': dictionary.memory,
    '[KERNEL]': dictionary.kernel,
    '[OS]': dictionary.os
}

def populate_yaml(filename,dic):
    flag = [0,0,0,0]
    bogo = 0
    for key,value in category.iteritems():
        value(dic)
    with open(filename,'r') as infp:
        content = infp.read()
        contents = content.split('\n\n\n')
        for blocks in contents:
            if blocks != '':
                group = re.search(r'(\d+)[.]([\w /]+)', blocks)

                if group.group(2) == "lscpu":
                    lscpu_list.sort()
                    key_lists = dic['Hardware_Info']['CPU'].keys()
                    key_lists.sort()
                    #for items, key in key_list, dic['Hardware_Info']['CPU'].iteritems():
                    for i in range(0,len(lscpu_list)):
                        command =  str(lscpu_list[i]) + ':' +"\s+([\w\S ]+)"

                        group_keys = re.search(command,blocks,re.I)

                        if lscpu_list[i] != 'BogoMIPS' or bogo == 0:
                            try:
                                dic['Hardware_Info']['CPU'][key_lists[i]] = group_keys.group(1)
                            except:
                                dic['Hardware_Info']['CPU'][key_lists[i]] = "*TBA"
                    if bool(re.search(r'\s+L1d cache:\s([\w\S ]+)',blocks)):
                        asd = re.search(r'\s+L1d cache:\s([\w\S ]+)',blocks)
                        dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size'] = asd.group(1).strip()
                        flag[0] += 1
                    else:
                        dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size'] = "*TBA"
                    if bool(re.search(r'\s+L1i cache:\s([\w\S ]+)',blocks)):
                        asd = re.search(r'\s+L1i cache:\s([\w\S ]+)',blocks)
                        dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size'] = asd.group(1).strip()
                        flag[1] += 1
                    else:
                        dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size'] = "*TBA"
                    if bool(re.search(r'\s+L2 cache:\s([\w\S ]+)',blocks)):
                        asd = re.search(r'\s+L2 cache:\s([\w\S ]+)',blocks)
                        dic['Hardware_Info']['MEMORY']['L2_Cache_Size'] = asd.group(1).strip()
                        flag[2] += 1
                    else:
                        dic['Hardware_Info']['MEMORY']['L2_Cache_Size'] = "*TBA"
                    if bool(re.search(r'\s+L3 cache:\s([\w\S ]+)',blocks)):
                        asd = re.search(r'\s+L3 cache:\s([\w\S ]+)',blocks)
                        dic['Hardware_Info']['MEMORY']['L3_Cache_Size'] = asd.group(1).strip()
                        flag[3] += 1
                    else:
                        dic['Hardware_Info']['MEMORY']['L3_Cache_Size'] = "*TBA"
                    continue

                elif re.search("cat /proc/cpuinfo",blocks):
                    if bool(re.search(r'\s+BogoMIPS\s+:\s+([\w\S ]+)',blocks)):
                        asd = re.search(r'\s+BogoMIPS\s+:\s+([\w\S ]+)',blocks,re.I)
                        dic['Hardware_Info']['CPU']['BogoMIPS'] = asd.group(1).strip()
                        bogo = bogo+1
                
                elif group.group(2).strip() == "lsb_release":
                    lsb_release_list.sort()
                    key_lists = dic['Hardware_Info']['OS'].keys()
                    key_lists.sort()
                    for i in range(0,len(lsb_release_list)):
                        command = str(lsb_release_list[i]) + ':' +"\s+([\w\S ]+)"
                        group_keys = re.search(command,blocks)
                        try:
                            dic['Hardware_Info']['OS'][key_lists[i]] = group_keys.group(1)
                        except:
                            dic['Hardware_Info']['OS'][key_lists[i]] = "*TBA"
                    continue
                
                elif group.group(2).strip() == "lspci":
                    lspci_list.sort()
                    key_lists = dic['Hardware_Info']['NETWORK'].keys()
                    key_lists.sort()
                    pci_info = []
                    for i in range(0,len(key_lists)):
                        pci_details = "*TBA"
                        if bool(re.search(r'Ethernet controller \[0200\]:\s+([\w\S ]+ )',blocks)):
                            group_keys = re.findall(r'Ethernet controller \[0200\]:\s+([\w\S ]+ )',blocks)
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
                
                elif group.group(2).strip() == "uname":
                    key_lists = dic['Hardware_Info']['KERNEL'].keys()
                    key_lists.sort()
                    for i in range(0,len(key_lists)):
                        blocks = blocks.splitlines()
                        output = blocks[3].split(' ')[2]
                        try:
                            dic['Hardware_Info']['KERNEL'][key_lists[i]] = output
                        except:
                            dic['Hardware_Info']['KERNEL'][key_lists[i]] = "*TBA"
                    continue
                elif group.group(2).strip() == "dmidecode":
                    block = blocks.split('\n\n')
                    i = 0 
                    for item in block:
                        if bool(re.search(r'Memory Device\n',item)):
                            i = i+1
                            if i < 2 :
                                continue
                            if i> 3 :
                                break
                            if bool(re.search(r'\s+Form Factor:\s([\w\S ]+)',item)):
                                asd = re.search(r'\s+Form Factor:\s([\w\S ]+)',item)
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Formfactor'] = asd.group(1).strip()
                            else:
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Formfactor'] = "*TBA"

                            if bool(re.search(r'\s+Type:\s([\w\S ]+)',item)):
                                asd = re.search(r'\s+Type:\s([\w\S ]+)',item)
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Type'] = asd.group(1).strip()
                            else:
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Type'] = "*TBA"

                            if bool(re.search(r'\s+Speed:\s([\w\S ]+)',item)):
                                asd = re.search(r'\s+Speed:\s([\w\S ]+)',item)
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Max_Speed'] = asd.group(1).strip()
                            else:
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Max_Speed'] = "*TBA"

                            if bool(re.search(r'\s+Manufacturer:\s([\w\S ]+)',item)):
                                asd = re.search(r'\s+Manufacturer:\s([\w\S ]+)',item)
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Manufactuer'] = asd.group(1).strip()
                            else:
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Formfactor'] = "*TBA"

                            if bool(re.search(r'\s+Part Number:\s([\w\S ]+)',item)):
                                asd = re.search(r'\s+Part Number:\s([\w\S ]+)',item)
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Part_number'] = asd.group(1).strip()
                            else:
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Part_number'] = "*TBA"

                            if bool(re.search(r'\s+Configured Clock Speed:\s([\w\S ]+)',item)):
                                asd = re.search(r'\s+Configured Clock Speed:\s([\w\S ]+)',item)
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Current_Speed'] = asd.group(1).strip()
                            else:
                                dic['Hardware_Info']['MEMORY']['Main_Memory_Current_Speed'] = dic['Hardware_Info']['MEMORY']['Main_Memory_Max_Speed']
                                       
                                
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
                    continue                        
                elif group.group(2).strip() == "lshw":
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
                    if bool(re.search(r'sda\s+([\d.]+G)[\w\S ]+',blocks)):
                        asd = re.search(r'sda\s+([\d.]+G)[\w\S ]+',blocks)
                        print asd.group(1).strip()
                        dic['Hardware_Info']['DISK']['sda_Size']= asd.group(1).strip()
                    if bool(re.search(r'sdb\s+([\d.]+G)[\w\S ]+',blocks)):
                        asd = re.search(r'sdb\s+([\d.]+G)[\w\S ]+',blocks)
                        dic['Hardware_Info']['DISK']['sdb_Size']= asd.group(1).strip()


                    continue    
    return



def update(dic,filename):
    update_list = ['Unknown','Notspecified',0,'']
    for hardware_info,category_dic in dic.iteritems():
        for category,info_dic in category_dic.iteritems():
            for key,value in info_dic.iteritems():
                if value in update_list:
                    dic[hardware_info][category][key] = "*TBA"
    files = ['./HardwareInfo/D02-32G_Targetinfo']
    if filename in files:
        cores = int(dic['Hardware_Info']['CPU']['CPU_Cores'])
        cached = int(dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size'].split(' ')[0])
        cachei = int(dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size'].split(' ')[0])
        cached = str(cached/cores) + ' kB'
        cachei = str(cachei/cores) + ' kB'

        dic['Hardware_Info']['MEMORY']['L1_D-Cache_Size'] = cached
        dic['Hardware_Info']['MEMORY']['L1_I-Cache_Size'] = cachei

    out_file = filename.split('/')[-1] + ".yaml"
    output_file = os.path.join(out_path,out_file)
    with open(output_file,'w') as outfp:
        outfp.write(yaml.dump(dic,default_flow_style=False))

    return 

'''
if __name__ == "__main__":
    category = {
        '[CPU]' : dictionary.cpu,
        '[DISK]' : dictionary.disk,
        '[NETWORK]' : dictionary.network,
        '[MEMORY]' : dictionary.memory,
        '[KERNEL]' : dictionary.kernel,
        '[OS]' : dictionary.os
    }
    dic = {}
    for filename in glob.glob(os.path.join(path, '*_Targetinfo')):
        print filename
        populate_yaml(filename,dic)
        update(dic,filename)
'''