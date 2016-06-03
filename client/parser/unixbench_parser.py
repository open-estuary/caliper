import re
import yaml
def unixbench_parser(contents, outfp):
    seperators ={'ub_Dhrystone':'Dhrystone 2 using register variables',
                 'ub_Whetstone':'Double-Precision Whetstone',
                 'ub_Execl_Throughput':'Execl Throughput',
                 'ub_File_Cpy_1024buf_2000blk':'File Copy 1024 bufsize 2000 maxblocks',
                 'ub_File_Cpy_256buf_500blk':'File Copy 256 bufsize 500 maxblocks',
                 'ub_File_Cpy_4096buf_8000blk':'File Copy 4096 bufsize 8000 maxblocks',
                 'ub_pipe_Throughput':'Pipe Throughput',
                 'ub_pipe_ctx':'Pipe-based Context Switching',
                 'ub_Process_Creation':'Process Creation',
                 'ub_shell_script_1_concurrent':'Shell Scripts \(1 concurrent\)',
                 'ub_shell_script_8_concurrent':'Shell Scripts \(8 concurrent\)'}
    contents = contents.split("-----------------------------------------------------------------------")

    dic = {}
    dic['multicore'] = {}
    dic['sincore'] = {}
    for key,value in seperators.iteritems():
        dic['sincore'][key] = re.findall(value + r'\s+\d+.\d+\s+(\d+.\d+)',contents[1])[0]
        dic['multicore'][key] = re.findall(value + r'\s+\d+.\d+\s+(\d+.\d+)', contents[2])[0]

    outfp.write(yaml.dump(dic,default_flow_style=False))
    outfp.close()
    return dic