import re
import string
import pdb
import sys
import yaml
import logging


def get_value(tags, key_tags, content, outfp):
    flag = -1
    for i in range(0, len(tags)):
        if re.search(tags[i], content):
            flag = 0
            for line in content.splitlines():
                if re.search('seconds', line):
                    score_string = line.split(":")[-1].strip()
                    score = score_string.split()[0]
                    if string.atof(score):
                        outfp.write(key_tags[i] + ": " + score_string + "\n")
                        return score
            outfp.write(key_tags[i] + ": 0\n")
            return flag
    return flag


processor = ['lat_syscall', 'lat_read', 'lat_write', 'lat_stat',
            'lat_openclose', 'lat_tcp_select', 'lat_siginstall',
            'lat_sigcatch', 'lat_nullproc', 'lat_simpleproc', 'lat_shproc']

pro_dic = {'lat_syscall': 'null_call', 'lat_read': 'null_IO',
            'lat_write': 'null_IO',
            'lat_stat': 'stat', 'lat_openclose': 'open_close',
            'lat_tcp_select': 'slct_TCP', 'lat_siginstall': 'sig_inst',
            'lat_sigcatch': 'sig_hndl', 'lat_nullproc': 'fork_proc',
            'lat_simpleproc': 'exec_proc', 'lat_shproc': 'sh_proc'}

int_label = ['integer_bit', 'integer_add', 'integer_mul',
            'integer_div', 'integer_mod']
int64_label = ['int64_bit', 'int64_add', 'int64_mul', 'int64_div', 'int64_mod']

float_label = ['float_add', 'float_mul', 'float_div', 'float_bogomflops']
double_label = ['double_add', 'double_mul', 'double_div', 'double_bogomflops']

ctx_label = ['lat_ctx0_2', 'lat_ctx16_2', 'lat_ctx64_2', 'lat_ctx16_8',
            'lat_ctx64_8', 'lat_ctx16_16', 'lat_ctx64_16']
ctx_label_dic = {'lat_ctx0_2': '02p/0K_ctxsw', 'lat_ctx16_2': '02p/16K_ctxsw',
                'lat_ctx64_2': '02p/64K_ctxsw', 'lat_ctx16_8': '08p/16K_ctxsw',
                'lat_ctx64_8': '08p/64K_ctxsw',
                'lat_ctx16_16': '16p/16K_ctxsw',
                'lat_ctx64_16': '16p/64K_ctxsw'}

ipc_local_label = ['lat_pipe', 'lat_unix', 'lat_udp_local',
                    'lat_rpc_udp_local', 'lat_tcp_local',
                    'lat_rpc_tcp_local', 'lat_tcp_connect_local']
ipc_local_dic = {'lat_pipe': 'Pipe', 'lat_unix': 'AF_Unix',
                'lat_udp_local': 'UDP',# 'lat_rpc_udp_local': 'RPC/UDP',
                'lat_tcp_local': 'TCP',# 'lat_rpc_tcp_local': 'RPC/TCP',
                'lat_tcp_connect_local': 'TCP_con'}

ipc_remote_label = ['lat_udp_remote', 'lat_rpc_udp_remote', 'lat_tcp_remote',
                    'lat_rpc_tcp_remote', 'lat_tcp_connect_remote']
ipc_remote_dic = {'lat_udp_remote': 'UDP', 'lat_rpc_udp_remote': 'RPC/UDP',
                    'lat_tcp_remote': 'TCP', 'lat_rpc_tcp_remote': 'RPC/TCP',
                    'lat_tcp_connect_remote': 'TCP_con'}

file_vm_label = ['fs_create_0k', 'fs_create_10k', 'fs_delete_0k',
                    'fs_delete_10k', 'lat_mappings', 'lat_protfault',
                    'lat_pagefault', 'lat_fd_select']
file_vm_dic = {'fs_create_0k': '0k_file_create',
                'fs_create_10k': '10k_file_create',
                'fs_delete_0k': '0k_file_delete',
                'fs_delete_10k': '10k_file_delete',
                'lat_mappings': 'Mmap(KB)', 'lat_protfault': 'Prot_fault',
                'lat_pagefault': 'Page_Fault',
                'lat_fd_select': '100fd_select'}

bw_ipc_label = ['bw_pipe', 'bw_unix', 'bw_tcp_local', 'bw_reread',
                'bw_bcopy_libc', 'bw_bcopy_unrolled', 'bw_mmap',
                'bw_mem_rdsum', 'bw_mem_wr',
                'bw_reread_open2close',
                'bw_mmap_readopen2close', 'bw_bcopy_libc_aligned',
                'bw_mem_bzero', 'bw_bcopy_unrolled_partial',
                'bw_mem_rdsum_partial', 'bw_mem_wr_partial',
                'bw_mem_wr_rd_partial']
bw_ipc_dic = {'bw_pipe': 'Pipe', 'bw_unix': 'AF_Unix', 'bw_tcp_local': 'TCP',
                'bw_reread': 'File_reread', 'bw_bcopy_libc': 'Bcopy(libc)',
                'bw_bcopy_unrolled': 'Bcopy(hand)',
                'bw_mem_rdsum': 'Mem_read',
                'bw_mem_wr': 'Mem_write', 'bw_mmap': 'Mmap_reread',
                'bw_reread_open2close': 'Reread_open2close',
                'bw_mmap_readopen2close': 'Mmap_open2close',
                'bw_bcopy_libc_aligned': 'Bcopy(libc_a)',
                'bw_mem_bzero': 'Bzero',
                'bw_bcopy_unrolled_partial': 'BCopy(hand_partial)',
                'bw_mem_rdsum_partial': 'Mem_read_partial',
                'bw_mem_wr_partial': 'Mem_write_partial',
                'bw_mem_wr_rd_partial': 'Mem_RW_partial'}

mem_latency = ['lat_l1', 'lat_l2', 'lat_mem']
mem_lat_dic = {'lat_l1': 'L1', 'lat_l2': 'L2', 'lat_mem': 'Main_memory'}

local_mem_lat_label = ['lat_0_5KB', 'lat_1KB', 'lat_2KB', 'lat_3KB', 'lat_4KB', 
			'lat_6KB', 'lat_8KB', 'lat_12KB', 'lat_16KB', 'lat_24KB', 
			'lat_32KB', 'lat_48KB', 'lat_64KB', 'lat_96KB', 'lat_128KB', 
			'lat_192KB', 'lat_256KB', 'lat_384KB', 'lat_512KB', 'lat_768KB',
			'lat_1MB', 'lat_1_5MB', 'lat_2MB', 'lat_3MB', 'lat_4MB', 
			'lat_6MB', 'lat_8MB', 'lat_12MB', 'lat_16MB', 'lat_24MB', 
			'lat_32MB']

local_mem_lat_dic = {'lat_0_5KB': 'lb_lat_00_0.5KB',
                     'lat_1KB': 'lb_lat_01_01KB',
                     'lat_2KB': 'lb_lat_02_2KB',
                     'lat_3KB': 'lb_lat_03_3KB',
                     'lat_4KB': 'lb_lat_04_4KB',
                     'lat_6KB': 'lb_lat_05_6KB',
                     'lat_8KB': 'lb_lat_06_8KB',
                     'lat_12KB': 'lb_lat_07_12KB',
                     'lat_16KB': 'lb_lat_08_16KB',
                     'lat_24KB': 'lb_lat_09_24KB',
                     'lat_32KB': 'lb_lat_10_32KB',
                     'lat_48KB': 'lb_lat_11_48KB',
                     'lat_64KB': 'lb_lat_12_64KB',
                     'lat_96KB': 'lb_lat_13_96KB',
                     'lat_128KB': 'lb_lat_14_128KB',
                     'lat_192KB': 'lb_lat_15_192KB',
                     'lat_256KB': 'lb_lat_16_256KB',
                     'lat_384KB': 'lb_lat_17_384KB',
                     'lat_512KB': 'lb_lat_18_512KB',
                     'lat_768KB': 'lb_lat_19_768KB',
                     'lat_1MB': 'lb_lat_20_1MB',
                     'lat_1_5MB': 'lb_lat_21_1.5MB',
                     'lat_2MB': 'lb_lat_22_2MB',
                     'lat_3MB': 'lb_lat_23_3MB',
                     'lat_4MB': 'lb_lat_24_4MB',
                     'lat_6MB': 'lb_lat_25_6MB',
                     'lat_8MB': 'lb_lat_26_8MB',
                     'lat_12MB': 'lb_lat_27_12MB',
                     'lat_16MB': 'lb_lat_28_16MB',
                     'lat_24MB': 'lb_lat_29_24MB',
                     'lat_32MB': 'lb_lat_30_32MB'}

mb = 1000000
kb = 1000


def lmbench_lat_parser(content, outfp):
    dic = {}
    dic['cpu_sincore'] = {}
    dic['cpu_sincore']['sincore_int'] = {}
    dic['cpu_sincore']['sincore_float'] = {}
    dic['cpu_sincore']['sincore_double'] = {}
    dic['latency'] = {}
    dic['latency']['process'] = {}
    dic['latency']['ctx'] = {}
    dic['latency']['file/vm'] = {}
    # dic['latency']['mem'] = {}
    dic['network'] = {}
    dic['network']['local_lat'] = {}
    # dic['network']['remote_lat'] = {}

    dic_processor = {}
    dic_int = {}
    dic_int64 = {}
    dic_float = {}
    dic_double = {}
    dic_context = {}
    dic_local_lat = {}
    dic_remote_lat = {}
    dic_mem_lat = {}
    dic_file_vm = {}
    lat_mem_rd_type = 0

    for block in content.split('\n\n'):
        orig_block = block
        for line in block.splitlines():
            if not line:
                continue
            try:
                num = line.split()[-2]
            except Exception:
                pass

            if re.search('^Select on 100 tcp fd', line):
                dic_processor[pro_dic['lat_tcp_select']] = num
            elif re.search('^Simple read:', line):
                dic_processor[pro_dic['lat_read']] = num
            elif re.search('^Simple write:', line):
                if dic_processor[pro_dic['lat_read']]:
                    dic_processor[pro_dic['lat_write']] =\
                            float(dic_processor[pro_dic['lat_read']]) +\
                                                float(num) / 2
            elif re.search('^Simple stat:', line):
                dic_processor[pro_dic['lat_stat']] = num
            elif re.search('^Simple open.close:', line):
                dic_processor[pro_dic['lat_openclose']] = num
            elif re.search('^Null syscall:', line):
                dic_processor[pro_dic['lat_write']] = num
            elif re.search('^Simple syscall:', line):
                dic_processor[pro_dic['lat_syscall']] = num
            elif re.search('^Signal handler installation:', line):
                dic_processor[pro_dic['lat_siginstall']] = num
            elif re.search('^Signal handler overhead:', line):
                dic_processor[pro_dic['lat_sigcatch']] = num
            elif re.search('^Process fork.exit', line):
                dic_processor[pro_dic['lat_nullproc']] = num
            elif re.search('^Process fork.execve:', line):
                dic_processor[pro_dic['lat_simpleproc']] = num
            else:
                if re.search('^Process fork..bin.sh', line):
                    dic_processor[pro_dic['lat_shproc']] = num

            if re.search('^integer bit:', line):
                dic_int['integer_bit'] = num
            elif re.search('^integer add:', line):
                dic_int['integer_add'] = num
            elif re.search('^integer mul:', line):
                dic_int['integer_mul'] = num
            elif re.search('^integer div:', line):
                dic_int['integer_div'] = num
            else:
                if re.search('^integer mod:', line):
                    dic_int['integer_mod'] = num

            if re.search('^int64 bit:', line):
                dic_int64['int64_bit'] = num
            elif re.search('^int64 add:', line):
                dic_int64['int64_add'] = num
            elif re.search('^int64 mul:', line):
                dic_int64['int64_mul'] = num
            elif re.search('^int64 mod:', line):
                dic_int64['int64_mod'] = num
            else:
                if re.search('^int64 div:', line):
                    dic_int64['int64_div'] = num

            if re.search('^float add:', line):
                dic_float['float_add'] = num
            elif re.search('^float mul:', line):
                dic_float['float_mul'] = num
            elif re.search('^float div:', line):
                dic_float['float_div'] = num
            elif re.search('^double add:', line):
                dic_double['double_add'] = num
            elif re.search('^double mul:', line):
                dic_double['double_mul'] = num
            elif re.search('^double div:', line):
                dic_double['double_div'] = num
            elif re.search('^float bogomflops:', line):
                dic_float['float_bogomflops'] = num
            else:
                if re.search('^double bogomflops:', line):
                    dic_double['double_bogomflops'] = num

            if re.search('^Pipe latency:', line):
                dic_local_lat[ipc_local_dic['lat_pipe']] = num
            if re.search('AF_UNIX sock stream latency:', line):
                dic_local_lat[ipc_local_dic['lat_unix']] = num
            if re.search('UDP latency using localhost:', line):
                dic_local_lat[ipc_local_dic['lat_udp_local']] = num
            else:
                if re.search('UDP latency using', line):
                    dic_remote_lat[ipc_remote_dic['lat_udp_remote']] = num
            if re.search('TCP latency using localhost:', line):
                dic_local_lat[ipc_local_dic['lat_tcp_local']] = num
            else:
                if re.search('TCP latency using', line):
                    dic_remote_lat[ipc_remote_dic['lat_tcp_remote']] = num
            #if re.search('RPC.udp latency using localhost:', line):
            #    dic_local_lat[ipc_local_dic['lat_rpc_udp_local']] = num
            #else:
            #    if re.search('RPC.udp latency using', line):
            #        dic_remote_lat[ipc_remote_dic['lat_rpc_udp_remote']] = num
            #if re.search('RPC.tcp latency using localhost:', line):
            #    dic_local_lat[ipc_local_dic['lat_rpc_tcp_local']] = num
            #else:
            #    if re.search('RPC.tcp latency using', line):
            #        dic_remote_lat[ipc_remote_dic['lat_rpc_tcp_remote']] = num
            if re.search('TCP.IP connection cost to localhost:', line):
                dic_local_lat[ipc_local_dic['lat_tcp_connect_local']] = num
            else:
                if re.search('TCP.IP connection cost to', line):
                    dic_remote_lat[ipc_remote_dic['lat_tcp_connect_remote']]\
                            = num

            if re.search('^Pagefaults on', line):
                dic_file_vm[file_vm_dic['lat_pagefault']] = num
            if re.search('^Protection fault:', line):
                dic_file_vm[file_vm_dic['lat_protfault']] = num
            if re.search('^Select on 100 fd', line):
                dic_file_vm[file_vm_dic['lat_fd_select']] = num

            if re.search('^"mappings', line):
                value = get_last_value(orig_block)
                dic_file_vm[file_vm_dic['lat_mappings']] = value

            if re.search('^"File system latency', line):
                for subline in orig_block.splitlines():
                    if re.search('^0k', subline):
                        dic_file_vm[file_vm_dic['fs_create_0k']] = mb /\
                                float(subline.split()[2])
                        dic_file_vm[file_vm_dic['fs_delete_0k']] = mb /\
                                float(subline.split()[3])
                    if re.search('^1k', subline):
                        pass
                    if re.search('^4k', subline):
                        pass
                    if re.search('^10k', subline):
                        dic_file_vm[file_vm_dic['fs_create_10k']] = mb /\
                                float(subline.split()[2])
                        dic_file_vm[file_vm_dic['fs_delete_10k']] = mb /\
                                float(subline.split()[3])

            if re.search('size=0', line):
                for subline in orig_block.splitlines():
                    if not subline:
                        continue
                    ctx_value = subline.split()[1]
                    if re.search('^2 ', subline):
                        dic_context[ctx_label_dic['lat_ctx0_2']] = ctx_value
                        break
                    # elif re.search('^8', subline):
                    #    dic_context[ctx_label_dic['lat_ctx0_8']] = ctx_value
                    # else:
                    #    if re.search('^16', subline):
                    #        dic_context[ctx_label_dic['lat_ctx0_16']] = \
                    #        ctx_value
            if re.search('size=16', line):
                for subline in orig_block.splitlines():
                    if subline:
                        try:
                            ctx_value = subline.split()[1]
                        except IndexError:
                            continue
                    if re.search('^2 ', subline):
                        dic_context[ctx_label_dic['lat_ctx16_2']] = ctx_value
                    elif re.search('^8 ', subline):
                        dic_context[ctx_label_dic['lat_ctx16_8']] = ctx_value
                    else:
                        if re.search('^16 ', subline):
                            dic_context[ctx_label_dic['lat_ctx16_16']] = \
                                    ctx_value

            if re.search('size=64', line):
                for subline in orig_block.splitlines():
                    ctx_value = subline.split()[1]
                    if re.search('^2 ', subline):
                        dic_context[ctx_label_dic['lat_ctx64_2']] = ctx_value
                    elif re.search('^8 ', subline):
                        dic_context[ctx_label_dic['lat_ctx64_8']] = ctx_value
                    else:
                        if re.search('^16 ', subline):
                            dic_context[ctx_label_dic['lat_ctx64_16']] = \
                                    ctx_value

            if re.search('^Memory load latency', line):
                lat_mem_rd_type = 1
            if re.search('^Random load latency', line):
                lat_mem_rd_type = 2
            if re.search('^"stride=128', line):
                size = 0
                save = 0
                for subline in orig_block.splitlines():
                    try:
                        size = subline.split()[0]
                        save = subline.split()[1]
                    except Exception:
                        continue

             #       if re.search('0.00098', subline):
             #           if (lat_mem_rd_type == 1):
             #               dic_mem_lat[mem_lat_dic['lat_l1']] = save
             #       else:
             #           if re.search('0.12500', subline):
             #               if (lat_mem_rd_type == 1):
             #                   dic_mem_lat[mem_lat_dic['lat_l2']] = save
             #   if (size < 0.8):
             #      logging.info('$file: No 8MB memory latency,using $size\n')
             #   if (lat_mem_rd_type == 1):
             #       dic_mem_lat[mem_lat_dic['lat_mem']] = save

            # if re.search('^"stride=16', line):
            #    size = 0
            #    save = 0
            #    for subline in orig_block.splitlines():
            #        try:
            #            size = subline.split()[0]
            #            save = subline.split()[1]
            #        except Exception:
            #            continue
            #    if (size < 0.8):
            #        logging.info('$file: No 8MB memory latency,
            #                      using $size\n')
            #    if (lat_mem_rd_type == 2):
            #        dic_mem_lat[mem_lat_dic['lat_mem_rand']] = save
    if dic_int:
        dic['cpu_sincore']['sincore_int'] = dic_int
    if dic_float:
        dic['cpu_sincore']['sincore_float'] = dic_float
    if dic_double:
        dic['cpu_sincore']['sincore_double'] = dic_double
    if dic_processor:
        dic['latency']['process'] = dic_processor
    if dic_context:
        dic['latency']['ctx'] = dic_context
    if dic_local_lat:
        dic['network']['local_lat'] = dic_local_lat
    if dic_mem_lat:
        dic['latency']['mem'] = dic_mem_lat
    if dic_file_vm:
        dic['latency']['file/vm'] = dic_file_vm
    outfp.write(yaml.dump(dic, default_flow_style=False))
    return dic


def get_last_value(block):
    lines = block.split('\n')
    value = 0
    for cnt in range(len(lines)-1, 0, -1):
        if not lines[cnt]:
            continue
        if lines[cnt]:
            num2 = lines[cnt].split()[1]
            num1 = lines[cnt].split()[0]
            try:
                value = float(num2) / float(num1)
            except:
                continue
            else:
                return value
    return value


def get_biggest(block):
    lines = block.splitlines()
    value = 0
    for i in range(len(lines)-1, 0, -1):
        if lines[i] and re.findall('\d+', lines[i]):
            value = lines[i].split()[1]
            return value
    return value


def lmbench_bandwidth_parser(content, outfp):
    dic = {}
    dic['memory'] = {}
    dic['memory']['local_speed'] = {}

    dic_mem_speed = {}

    for block in content.split('\n\n'):
        orig_block = block
        for line in block.splitlines():
            if not line:
                continue
            if re.search('^Socket bandwidth using localhost', line):
                num = line.split()[1]
                dic_mem_speed[bw_ipc_dic['bw_tcp_local']] = \
                        get_biggest(orig_block)
            if re.search('^AF_UNIX sock stream bandwidth:', line):
                num = line.split()[-2]
                dic_mem_speed[bw_ipc_dic['bw_unix']] = num
            if re.search('^Pipe bandwidth', line):
                num = line.split()[-2]
                dic_mem_speed[bw_ipc_dic['bw_pipe']] = num
            # if re.search('^File .* write bandwidth', line):
            #    num = line.split()[-2]
            #    dic_mem_speed = num
            if re.search('^"read bandwidth', line):
                dic_mem_speed[bw_ipc_dic['bw_reread']] = \
                        get_biggest(orig_block)
            if re.search('^"Mmap read bandwidth', line):
                dic_mem_speed[bw_ipc_dic['bw_mmap']] = get_biggest(orig_block)
            if re.search('^"libc bcopy unaligned', line):
                dic_mem_speed[bw_ipc_dic['bw_bcopy_libc']] = \
                        get_biggest(orig_block)
            if re.search('^"unrolled bcopy unaligned', line):
                dic_mem_speed[bw_ipc_dic['bw_bcopy_unrolled']] = \
                        get_biggest(orig_block)
            if re.search('^Memory read', line):
                dic_mem_speed[bw_ipc_dic['bw_mem_rdsum']] = \
                        get_biggest(orig_block)
            if re.search('^Memory write', line):
                dic_mem_speed[bw_ipc_dic['bw_mem_wr']] = \
                        get_biggest(orig_block)

            if re.search('^"read open2close bandwidth', line):
                dic_mem_speed[bw_ipc_dic['bw_reread_open2close']] = \
                        get_biggest(orig_block)
            if re.search('^"Mmap read open2close bandwidth', line):
                dic_mem_speed[bw_ipc_dic['bw_mmap_readopen2close']] = \
                        get_biggest(orig_block)
            if re.search('^"libc bcopy aligned', line):
                dic_mem_speed[bw_ipc_dic['bw_bcopy_libc_aligned']] = \
                        get_biggest(orig_block)
            if re.search('^Memory bzero bandwidth', line):
                dic_mem_speed[bw_ipc_dic['bw_mem_bzero']] = \
                        get_biggest(orig_block)
            if re.search('^"unrolled partial bcopy unaligned', line):
                dic_mem_speed[bw_ipc_dic['bw_bcopy_unrolled_partial']] = \
                        get_biggest(orig_block)
            if re.search('^Memory partial read', line):
                dic_mem_speed[bw_ipc_dic['bw_mem_rdsum_partial']] = \
                        get_biggest(orig_block)
            if re.search('^Memory partial write', line):
                dic_mem_speed[bw_ipc_dic['bw_mem_wr_partial']] = \
                        get_biggest(orig_block)
            if re.search('^Memory partial read/write', line):
                dic_mem_speed[bw_ipc_dic['bw_mem_wr_rd_partial']] = \
                        get_biggest(orig_block)
    if dic_mem_speed:
        dic['memory']['local_speed'] = dic_mem_speed
    outfp.write(yaml.dump(dic, default_flow_style=False))
    return dic


def syscall_latency_parser(content, outfp):
    tags = ["null", "read", "write", "fstat", "stat", "open"]
    key_tags = ["lat_sys_null", "lat_sys_read", "lat_sys_wr", "lat_sys_fstat",
                "lat_sys_stat", "lat_sys_open/close"]

    tags_sig = ["install", "catch"]
    key_tags_sig = ["lat_sig_install", "lat_sig_catch"]

    tags_proc = ["fork\+exit", "fork\+execve", "shell"]
    key_tags_proc = ["lat_proc_fork", "lat_proc_exec", "lat_proc_shell"]

    score = 0
    if re.search("lat_syscall", content):
        score = get_value(tags, key_tags, content, outfp)
    elif re.search("lat_sig", content):
        score = get_value(tags_sig, key_tags_sig, content, outfp)
    elif re.search("lat_proc", content):
        score = get_value(tags_proc, key_tags_proc, content, outfp)
    else:
        score = -1
    return score


def network_latency_parser(content, outfp):
    tags_net = ["lat_pipe", "lat_unix", "lat_udp", "lat_tcp", "lat_connect"]
    score = 0
    score = get_value(tags_net, tags_net, content, outfp)
    return score


def get_last_num(content):
    score = 0
    lines = content.splitlines()
    for i in range(len(lines)-1, -1, -1):
        if not lines[i]:
            continue
        fields = lines[i].split()
        if len(fields):
            field = []
            for x in fields:
                try:
                    num = string.atof(x)
                    field.append(num)
                except BaseException:
                    continue
            if len(field):
                return field[-1]
    return score


def memory_speed_parser(content, outfp):
    score = 0
    if re.search(r"bw_mem.*\brd\b", content):
        score = get_last_num(content)
        outfp.write("bw_mem_rd: " + str(score) + "\n")
    elif re.search(r"bw_mem.*\bwr\b", content):
        score = get_last_num(content)
        outfp.write("bw_mem_wr: " + str(score) + "\n")
    elif re.search(r"bw_mem.*\brdwr\b", content):
        score = get_last_num(content)
        outfp.write("bw_mem_rdwr: " + str(score) + "\n")
    elif re.search(r"bw_mem.*\bbzero\b.?", content):
        score = get_last_num(content)
        outfp.write("bw_mem_bzero: " + str(score) + "\n")
    elif re.search(r"bw_mem.*\bbcopy\b", content):
        if not re.search(r"bw_mem.*\bbcopy\b\sconflict", content):
            score = get_last_num(content)
            outfp.write("bw_mem_bcopy: " + str(score) + "\n")
        else:
            score = -1
    else:
        score = -1
    return score

def lmbench_bandwidth_stream_v1(content, outfp):
    dic = {}                                    
    dic['copy'] = {}                     
    dic['scale'] = {}                     
    dic['add'] = {}                     
    dic['triad'] = {}                     
    score = 0

    for speed in re.findall("STREAM\s+copy\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream_bw_copy: " + str(score) + "\n")
        dic['copy'] = score 
    for speed in re.findall("STREAM\s+scale\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream_bw_scale: " + str(score) + "\n")
        dic['scale'] = score 
    for speed in re.findall("STREAM\s+add\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream_bw_add: " + str(score) + "\n")
        dic['add'] = score 
    for speed in re.findall("STREAM\s+triad\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream_bw_triad: " + str(score) + "\n")
        dic['triad'] = score
    return dic 

def lmbench_bandwidth_stream_v2(content, outfp):
    dic = {}                                    
    dic['fill'] = {}                     
    dic['copy'] = {}                     
    dic['daxpy'] = {}                     
    dic['sum'] = {}                     
    score = 0

    for speed in re.findall("STREAM2\s+fill\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream2_bw_fill: " + str(score) + "\n")
        dic['fill'] = score 
    for speed in re.findall("STREAM2\s+copy\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream2_bw_copy: " + str(score) + "\n")
        dic['copy'] = score 
    for speed in re.findall("STREAM2\s+daxpy\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream2_bw_daxpy: " + str(score) + "\n")
        dic['daxpy'] = score 
    for speed in re.findall("STREAM2\s+sum\s+bandwidth:\s+(.*?)MB/sec", content):
        score = string.atof(speed.strip())
        outfp.write("lmbench_stream2_bw_sum: " + str(score) + "\n")
        dic['sum'] = score 
    return dic 


def lmbench_latency_local_mem(content, outfp):
    dic = {}                                    

    for block in content.split('\n\n'):
        orig_block = block
        for line in block.splitlines():
            if not line:
                continue
 
            if re.search('^"stride=128', line):
                size = 0
                save = 0
                for subline in orig_block.splitlines():
                    try:
                        size = subline.split()[0]
                        save = subline.split()[1]
                    except Exception:
                        continue

                    if re.match('0.00049', subline):
                        dic[local_mem_lat_dic['lat_0_5KB']] = save
                    elif re.match('0.00098', subline):
                        dic[local_mem_lat_dic['lat_1KB']] = save
                    elif re.match('0.00195', subline):
                        dic[local_mem_lat_dic['lat_2KB']] = save
                    elif re.match('0.00293', subline):
                        dic[local_mem_lat_dic['lat_3KB']] = save
                    elif re.match('0.00391', subline):
                        dic[local_mem_lat_dic['lat_4KB']] = save
                    elif re.match('0.00586', subline):
                        dic[local_mem_lat_dic['lat_6KB']] = save
                    elif re.match('0.00781', subline):
                        dic[local_mem_lat_dic['lat_8KB']] = save
                    elif re.match('0.01172', subline):
                        dic[local_mem_lat_dic['lat_12KB']] = save
                    elif re.match('0.01562', subline):
                        dic[local_mem_lat_dic['lat_16KB']] = save
                    elif re.match('0.02344', subline):
                        dic[local_mem_lat_dic['lat_24KB']] = save
                    elif re.match('0.03125', subline):
                        dic[local_mem_lat_dic['lat_32KB']] = save
                    elif re.match('0.04688', subline):
                        dic[local_mem_lat_dic['lat_48KB']] = save
                    elif re.match('0.06250', subline):
                        dic[local_mem_lat_dic['lat_64KB']] = save
                    elif re.match('0.09375', subline):
                        dic[local_mem_lat_dic['lat_96KB']] = save
                    elif re.match('0.12500', subline):
                        dic[local_mem_lat_dic['lat_128KB']] = save
                    elif re.match('0.18750', subline):
                        dic[local_mem_lat_dic['lat_192KB']] = save
                    elif re.match('0.25000', subline):
                        dic[local_mem_lat_dic['lat_256KB']] = save
                    elif re.match('0.37500', subline):
                        dic[local_mem_lat_dic['lat_384KB']] = save
                    elif re.match('0.50000', subline):
                        dic[local_mem_lat_dic['lat_512KB']] = save
                    elif re.match('0.75000', subline):
                        dic[local_mem_lat_dic['lat_768KB']] = save
                    elif re.match('1.00000', subline):
                        dic[local_mem_lat_dic['lat_1MB']] = save
                    elif re.match('1.50000', subline):
                        dic[local_mem_lat_dic['lat_1_5MB']] = save
                    elif re.match('2.00000', subline):
                        dic[local_mem_lat_dic['lat_2MB']] = save
                    elif re.match('3.00000', subline):
                        dic[local_mem_lat_dic['lat_3MB']] = save
                    elif re.match('4.00000', subline):
                        dic[local_mem_lat_dic['lat_4MB']] = save
                    elif re.match('6.00000', subline):
                        dic[local_mem_lat_dic['lat_6MB']] = save
                    elif re.match('8.00000', subline):
                        dic[local_mem_lat_dic['lat_8MB']] = save
                    elif re.match('12.00000', subline):
                        dic[local_mem_lat_dic['lat_12MB']] = save
                    elif re.match('16.00000', subline):
                        dic[local_mem_lat_dic['lat_16MB']] = save
                    elif re.match('24.00000', subline):
                        dic[local_mem_lat_dic['lat_24MB']] = save
                    elif re.match('32.00000', subline):
                       dic[local_mem_lat_dic['lat_32MB']] = save
    
    outfp.write(yaml.dump(dic, default_flow_style=False))
    return dic          

def lmbench_bandwidth_parser_new(content, outfp):
    dic = {}
    dic['read'] = {}
    dic['fread'] = {}
    dic['write'] = {}
    dic['fwrite'] = {}
    dic['bzero'] = {}
    dic['readwrite'] = {}
    dic['copy'] = {}
    dic['fcopy'] = {}
    dic['bcopy'] = {}

    count = 0
    for block in content.split('\n\n'):
        orig_block = block
        for line in block.splitlines():

            if not line:
                continue

            if re.search('32.00', line):
                count += 1
                if count == 1:
                    dic['read'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_read: " + str(line.split()[1]) + "\n")
                if count == 2:
                    dic['fread'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_fread: " + str(line.split()[1]) + "\n")
                if count == 3:
                    dic['write'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_write: " + str(line.split()[1]) + "\n")
                if count == 4:
                    dic['fwrite'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_fwrite: " + str(line.split()[1]) + "\n")
                if count == 5:
                    dic['bzero'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_bzero: " + str(line.split()[1]) + "\n")
                if count == 6:
                    dic['readwrite'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_readwrite: " + str(line.split()[1]) + "\n")
                if count == 7:
                    dic['copy'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_copy: " + str(line.split()[1]) + "\n")
                if count == 8:
                    dic['fcopy'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_fcopy: " + str(line.split()[1]) + "\n")
                if count == 9:
                    dic['bcopy'] = line.split()[1]
                    outfp.write("lmbench_bandwidth_bcopy: " + str(line.split()[1]) + "\n")
                    break
    return dic

if __name__ == "__main__":
    infp = open(sys.argv[1], 'r')
    outfp = open("tmp.log", "w+")
    content = infp.read()
    # syscall_latency_parser(content, outfp)
    # network_latency_parser(content, outfp)
    # memory_speed_parser(content, outfp)
    pdb.set_trace()
    lmbench_lat_parser(content, outfp)
    #lmbench_bandwidth_parser(content, outfp)
    outfp.close()
    infp.close()
