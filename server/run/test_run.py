## wuyanjun w00291783
## wu.wu@hisilicon.com
## copyright

import ConfigParser
import os
import sys
import time
import shutil
import importlib
import yaml
import types
import string
import re
import pdb
import logging
import datetime
import subprocess

try:
    import caliper.common as common
except ImportError:
    import common

from caliper.server.compute_model.scores_method import Scores_method
from caliper.client.shared import error
from caliper.server import utils as server_utils
from caliper.client.shared import utils
from caliper.client.shared import caliper_path
from caliper.server.run import write_results

caliper_log_file = caliper_path.CALIPER_LOG_FILE

def get_server_command(kind_bench, section_name):
    server_config_file = ''
    bench_conf_dir = os.path.join(caliper_path.TESTS_CFG_DIR, kind_bench)

    server_config_file = server_utils.get_server_cfg_path(kind_bench)
    if server_config_file != '':
        server_config, server_sections = server_utils.read_config_file(server_config_file)
        if section_name in server_sections:
            command = server_config.get(section_name, 'command')
            logging.debug("command is %s" % command)
            return command
        else:
            return None
    else:
        return None

def run_all_cases(target_exec_dir, target, kind_bench, bench_name, 
                    run_file, parser):
    """
    function: run one benchmark which was selected in the configuration files
    """
    #get the abspath, which is the file name of run config for the benchmark
    bench_conf_file = os.path.join(caliper_path.TESTS_CFG_DIR,
                                    kind_bench, run_file)
    #get the config sections for the benchmrk
    configRun, sections_run = server_utils.read_config_file(bench_conf_file)
    logging.debug("the sections to run are: %s" % sections_run)
    if not os.path.exists(caliper_path.EXEC_LOG_DIR):
        os.mkdir(caliper_path.EXEC_LOG_DIR)
    log_bench = os.path.join(caliper_path.EXEC_LOG_DIR, bench_name)
    logfile = log_bench + "_output.log"
    tmp_log_file = log_bench + "_output_tmp.log"
    parser_result_file = log_bench + "_parser.log"
    tmp_parser_file = log_bench + "_parser_tmp.log"
    if os.path.exists(parser_result_file):
        os.remove(parser_result_file)
    if os.path.exists(logfile):
        os.remove(logfile)

    starttime = datetime.datetime.now()
    result = subprocess.call("echo '$$ %s EXECUTION START: %s' >> %s" 
                            % (bench_name, str(starttime)[:19],caliper_log_file), 
                            shell=True)
    #for each command in run config file, read the config for the benchmark
    for i in range(0, len(sections_run)):
        flag = 0
        try:
            category = configRun.get(sections_run[i], 'category')
            scores_way = configRun.get(sections_run[i], 'scores_way')
            parser = configRun.get(sections_run[i], 'parser')
            command = configRun.get(sections_run[i], 'command')
        except Exception:
            logging.debug("no value for the %s" % sections_run[i])
            continue

        if os.path.exists(tmp_parser_file):
            os.remove(tmp_parser_file)
        if os.path.exists(tmp_log_file):
            os.remove(tmp_log_file)
       
        server_run_command = get_server_command(kind_bench, sections_run[i])
        logging.debug("Get the server command is: %s" % server_run_command)
        ## run the command of the benchmarks
        try:
            flag = run_kinds_commands(sections_run[i], server_run_command, 
                                      tmp_log_file, kind_bench, target, command)
        except Exception, e:
            logging.info(e)
            server_utils.file_copy(logfile, tmp_log_file, 'a+') 
            os.remove(tmp_log_file)
            run_flag = server_utils.get_fault_tolerance_config(
                                'fault_tolerance', 'run_error_continue')
            if run_flag == 1:
                continue
            else:
                return result   
        else:
            server_utils.file_copy(logfile, tmp_log_file, 'a+') 
            if flag != 1:
                logging.info("There is wrong when running the command \"%s\"" 
                                % command)
                os.remove(tmp_log_file)

                run_flag = server_utils.get_fault_tolerance_config(
                                'fault_tolerance', 'run_error_continue')
                if run_flag == 1:
                    continue
                else:
                    return result   
        #parser the result in the tmp_log_file, the result is the output of 
        #running the command
        try:
            logging.debug("Parsering the result of command: %s" % command)
            parser_result = parser_case(kind_bench, bench_name, parser,
                                        tmp_log_file, tmp_parser_file)
        except Exception, e:
            logging.info("There is wrong when parsering the result of \" %s \"" 
                            % sections_run[i])
            logging.info(e)
            os.remove(tmp_parser_file)
            os.remove(tmp_log_file)
        else:
            server_utils.file_copy(parser_result_file, tmp_parser_file, "a+")
            os.remove(tmp_parser_file)
            os.remove(tmp_log_file)
            try:
                if ( parser_result < 0 ):
                    continue
            except Exception:
                if not parser_result:
                    continue

        # to compute the score    
        try:
            ## according the method in the config file, compute the score
            logging.debug("Computing the score of the result of command: %s" 
                            % command)
            flag_compute = compute_case_score(parser_result, category,
                                                scores_way, target)
        except Exception, e:
            logging.info(e)
            continue
        else:
            if not flag_compute:
                logging.info( "There is wrong when computing the result\
                                of \"%s\"" % command)
    # remove the parser file
    endtime = datetime.datetime.now()
    result = subprocess.call("echo '$$ %s EXECUTION STOP: %s' >> %s" 
                                % (sections_run[i], str(endtime)[:19], 
                                    caliper_log_file), shell=True)
    result = subprocess.call("echo '$$ %s EXECUTION DURATION %s Seconds'>>%s" 
                                % (sections_run[i], (endtime-starttime).seconds, 
                                    caliper_log_file), shell=True)
    pwd_parser = bench_name + "_parser.py"
    pwd_parserc= pwd_parser + 'c'
    if os.path.exists(pwd_parser):
        os.remove(pwd_parser)
    if os.path.exists(pwd_parserc):
        os.remove(pwd_parser+"c")

def run_commands(exec_dir, kind_bench, commands,
                    stdout_tee=None, stderr_tee=None, target=None):
    returncode = -1
    output = ''
   
    pwd = os.getcwd()
    os.chdir(exec_dir)
    try:
        # the commands is multiple lines, and was included by Quotation
        actual_commands = get_actual_commands(commands, target)
        try:
            logging.debug("the actual commands running in local is: %s" 
                            % actual_commands)
            result = utils.run(actual_commands, stdout_tee=stdout_tee,
                                stderr_tee=stderr_tee, verbose=True)
        except error.CmdError, e:
            raise error.ServRunError(e.args[0], e.args[1])
    except Exception, e:
        logging.debug( e )
    else:
        returncode = result.exit_status
        try:
            output = result.stdout
        except Exception:
            output = result.stderr
    os.chdir(pwd)
    return [output, returncode]

# normalize the commands
def get_actual_commands(commands, target):
    if commands is None or commands=='':
        return None
    
    post_commands = commands

    if re.findall('(\d+\.\d+\.\d+\.\d+)', commands):
        server_ip = server_utils.get_local_ip()
        last_ip = ""

        for each_ip in server_ip:
            items = each_ip.split(".")[0:2]
            pre = '.'.join(items)
            if target.ip.startswith(pre):
                last_ip = each_ip
                break
        if not last_ip:
            if len(server_ip) > 1:
                try:
                    server_ip.remove("127.0.0.1")
                except Exception:
                    raise e

            last_ip = server_ip[0]

        strinfo = re.compile('\d+\.\d+\.\d+\.\d+')
        post_commands = strinfo.sub(last_ip, commands)

    commands = post_commands

    if commands[0] == '\'' and commands[-1] == '\'':
        actual_commands = commands[1:-1]
    elif commands[0] == '\"' and commands[-1] == '\"':
        actual_commands = commands[1:-1]
    else:
        actual_commands = commands
    if actual_commands == '':
        return ''
    return actual_commands

def remote_commands_deal(commands, exec_dir, target):
    actual_commands = get_actual_commands(commands, target)
    final_commands = "cd %s; %s" % (exec_dir, actual_commands)
    logging.debug("The final command is %s" % final_commands)
    return final_commands

def run_remote_commands(exec_dir, kind_bench, commands, target,
                    stdout_tee=None, stderr_tee=None):
    returncode = -1
    output = ''
    try:
        # the commands is multiple lines, and was included by Quotation
        final_commands = remote_commands_deal(commands, exec_dir, target)
        if final_commands is not None and final_commands != '':
            logging.debug("the actual commands running on the remote host is: %s" 
                            % final_commands)
            result = target.run(final_commands, stdout_tee=stdout_tee,
                                stderr_tee=stderr_tee, verbose=True)
        else:
            return ['Not command specified', -1]
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    except Exception, e:
        logging.debug( e )
    else:
        returncode = result.exit_status
        try:
            output = result.stdout
        except Exception:
            output = result.stderr
    return [output, returncode]

def run_client_command(cmd_sec_name, tmp_logfile, kind_bench, target, command):
    fp = open(tmp_logfile, "a+")
    start_log = "%%%%%%          %s test start         %%%%%% \n" % cmd_sec_name
    fp.write(start_log)
    fp.write("<<<BEGIN TEST>>>\n")
    tags = "[test: " + cmd_sec_name + "]\n"
    fp.write(tags)
    logs = "log: " + get_actual_commands(command, target) + "\n"
    fp.write(logs)
    start = time.time()
    flag = 0
    logging.debug( "the client running command is %s" % command)
 
    # get the execution location in the remote host
    is_localhost = 0
    if server_utils.get_target_ip(target) in server_utils.get_local_ip():
        is_localhost = 1
    if (is_localhost == 1):
        arch = server_utils.get_local_machine_arch()
        host_exec_dir = os.path.join(caliper_path.GEN_DIR, arch)
    else:
        host_current_pwd = target.run("pwd").stdout.split("\n")[0]
        arch = server_utils.get_host_arch(target)
        host_exec_dir = os.path.join(host_current_pwd, 'caliper', "binary", arch)

    try:
        logging.debug("begining to execute the command of %s on the remote host"
                        % command)
        if (is_localhost == 1):
            logging.debug("client command in localhost is: %s" % command)
            [out, returncode] = run_commands(host_exec_dir, kind_bench,
                                                command, fp, fp)
        else:
            logging.debug("client command in localhost is: %s" % command)
            [out, returncode] = run_remote_commands(host_exec_dir, kind_bench, 
                                                    command, target, fp, fp)
    except error.ServRunError, e:
        fp.write( "[status]: FAIL\n")
        sys.stdout.write(e)
        flag = -1
    else:
        if not returncode:
            fp.write( "[status]: PASS\n")
            flag = 1
        else:
            fp.write( "[status]: FAIL\n")
            flag = 0
    end = time.time()
    interval = end - start
    fp.write("Time in Seconds: %.3fs\n" % interval)
    fp.write("<<<END>>>\n")
    fp.write("%%%%%% test_end %%%%%%\n\n")
    fp.close()
    return flag

def run_server_command(kind_bench, server_command, target):
    return_code = 0
    try:
        logging.debug("the server running command is %s" % server_command)
        local_arch = server_utils.get_local_machine_arch()
        local_exec_dir = os.path.join(caliper_path.GEN_DIR, local_arch)
        [output, return_code] = run_commands(local_exec_dir, kind_bench, 
                                                server_command, target)
    except Exception, e:
        logging.debug("There is wrong with running the server command: %s" 
                        % server_command)
        logging.info( e )
    else:
        os._exit(return_code)

def run_case(cmd_sec_name, server_command, tmp_logfile, kind_bench,
                target, command):
    if server_command is None or server_command=='':
        return
    if command is None or command =='':
        return

    while True:
        newpid = os.fork()
        logging.debug("the pid number is %d" % newpid)
        if newpid == 0:
            run_server_command(kind_bench, server_command, target)
        else:
            time.sleep(10)
            logging.debug("the pid number of parent is %d" % os.getpid())
            logging.debug("the pid number of child is %d" % newpid)
            try:
                return_code = run_client_command(cmd_sec_name, tmp_logfile, 
                                                    kind_bench,target, command)
            except Exception, e:
                logging.info("There is wrong with running the remote host\
                                command of %s" % command)
                logging.debug(e.args[0], e.args[1])
                utils.kill_process_tree(newpid)
            else:
                utils.kill_process_tree(newpid)
                return return_code
    return 0

def run_kinds_commands(cmd_sec_name, server_run_command, tmp_logfile, kind_bench,
                target, command):
    if server_run_command != '' and server_run_command is not None:
        logging.debug("Running the server_command: %s, and the client command: %s"
                            % (server_run_command, command))
        flag = run_case(cmd_sec_name, server_run_command, tmp_logfile,
                        kind_bench, target, command)
    else:
        logging.debug("only running the command %s in the remote host" % command)
        flag = run_client_command(cmd_sec_name, tmp_logfile, kind_bench,
                                    target, command)
    return flag

def parser_case(kind_bench, bench_name, parser, infile, outfile):
    if not os.path.exists(infile):
        return -1
    result = 0
    fp = open(outfile, "w")
    #the parser function defined in the config file is to filter the output.
    # get the abspth of the parser.py which is defined in the config files.
    pwd_file = bench_name + "_parser.py"
    parser_file = os.path.join(caliper_path.TESTS_CFG_DIR, kind_bench, pwd_file)
    if not os.path.exists(parser_file):
        fp.write("There is no such a file %s \n" % parser_file)
        sys.stdout.write("There is no such a file %s \n" % parser_file)
        return -2
    # copy the parser files to the cwd path to import it.
    pwd_parser = pwd_file.split(".")[0]
    shutil.copyfile(parser_file, pwd_file)
    result = 0 
    if os.path.isfile(parser_file):
        try:
            # import the parser module import_module
            parser_module = importlib.import_module(pwd_parser)
        except ImportError, e:
            logging.info( e )
            return -3
        try:
            methodToCall = getattr(parser_module, parser)
        except Exception, e:
            logging.info( e )
            return -4
        else:
            infp = open(infile, "r")
            outfp = open(outfile, 'a+')
            contents = infp.read()
            for content in re.findall("log:(.*?)\[status\]", contents, re.DOTALL):
                try:
                    # call the parser function to filter the output
                    logging.debug("Begining to parser the result of the case")
                    result = methodToCall(content, outfp)
                except Exception, e:
                    logging.info( e )
                    return -5
            outfp.close()
            infp.close()
    fp.close()
    # remove the parser file
    pwd_parser = bench_name + "_parser.py"
    pwd_parserc= pwd_parser + 'c'
    if os.path.exists(pwd_parser):
        os.remove(pwd_parser)
    if os.path.exists(pwd_parserc):
        os.remove(pwd_parser+"c")
    return result

def compute_case_score(result, category, score_way, target):
    tmp = category.split()
    length = len(tmp)
    # write the result and the corresponding score to files
    target_name = server_utils.get_host_name(target)
    yaml_dir = os.path.join(caliper_path.RESULTS_DIR, 'yaml')
    result_yaml_name = target_name + '.yaml'
    score_yaml_name = target_name + '_score.yaml'
    result_yaml = os.path.join(yaml_dir, result_yaml_name)
    score_yaml = os.path.join(yaml_dir, score_yaml_name)
    if (length==3 and tmp[0]=='Functional'):
        return compute_func(result, tmp, score_way, result_yaml, score_yaml)
    elif ((length != 0 and length <=4) and tmp[0]=='Performance'):
        return compute_perf(result, tmp, score_way, result_yaml, score_yaml)
    else:
        return -4

def compute_func(result, tmp, score_way, result_yaml, score_yaml):
    flag = 0
    try:
        flag = write_results.write_yaml_func(result_yaml, tmp, result, 0)
    except BaseException:
        logging.debug("There is wrong when computing the score")
    return flag

def compute_perf(result, tmp, score_way, result_yaml, score_yaml):
    result_flag = 1
    score_flag = 2

    if type(result) is types.StringType:
        if re.search('\+', result):
            result=result.replace('\+', 'e')
        result_fp = string.atof(result)
    elif type(result) is types.FloatType:
        result_fp = result
    elif type(result) is types.IntType:
        result_fp = result
    elif (type(result)==dict and (len(tmp)>0 and len(tmp)<4)):
        return deal_dic_for_yaml(result, tmp, score_way, result_yaml, score_yaml)
    else:
        return -4

    result_score = write_results.compute_score(score_way, result_fp)
    flag1 = 0
    flag2 = 0
    try:
        flag1 = write_results.write_yaml_perf(result_yaml, tmp, 
                                                result_fp, result_flag)
        flag2 = write_results.write_yaml_perf(score_yaml, 
                                                tmp, result_score, score_flag)
    except BaseException:
        logging.debug("There is wrong when compute the score.")
    return flag1 & flag2

def deal_dic_for_yaml(result, tmp, score_way, yaml_file, score_yaml_file):
    if (len(tmp) == 2):
        flag = write_results.write_dic(result, tmp, score_way, 
                                yaml_file, score_yaml_file )
    elif (len(tmp) == 3):
        flag = write_results.write_sin_dic(result, tmp, score_way, yaml_file,
                                            score_yaml_file)
    else:
        flag = write_results.write_multi_dic(result, tmp, score_way,
                                            yaml_file, score_yaml_file)
    return flag

def caliper_run( target_exec_dir, target):
    # get the test cases defined files
    config_files = server_utils.get_cases_def_files( target_exec_dir )
    logging.debug("the selected configuration are %s" % config_files)
   
    for i in range(0, len(config_files)):
        # run benchmarks selected in each configuration file
        config_file = os.path.join(caliper_path.CALIPER_DIR, config_files[i])
        config, sections = server_utils.read_config_file(config_file)
        logging.debug(sections)
        
        #get if it is the 'common' or 'arm' or 'android'
        classify = config_files[i].split("/")[-1].strip().split("_")[0]
        logging.debug(classify)

        for i in range(0, len(sections)):
            # run for each benchmark
            target_arch = server_utils.get_host_arch(target)
            build_name = sections[i]+'_'+target_arch+'.suc'
            build_suc = os.path.join(caliper_path.BUILD_LOG_DIR, build_name)
            if not os.path.exists(build_suc):
                continue
            build_host_name = sections[i] + '_' + \
                    server_utils.get_local_machine_arch() + '.fail'
            if os.path.exists(build_host_name):
                continue

            # try to resolve the configuration of the configuration file
            try:
                run_file = config.get(sections[i], 'run')
                parser = config.get(sections[i], 'parser')
            except Exception:
                raise AttributeError("The is no option value of parser")

            print_format()
            logging.info("Running %s" % sections[i])
            bench = os.path.join(classify, sections[i])
            try:
                result = run_all_cases(target_exec_dir, target, bench, 
                                        sections[i], run_file, parser)
            except Exception as ex:
                logging.info("Running %s Exception" % sections[i])
                print_format()
                run_flag = server_utils.get_fault_tolerance_config(
                                'fault_tolerance', 'run_error_continue')
                if run_flag == 1:
                    continue
                else:
                    return result
            else:
                logging.info("Running %s Finished" % sections[i])
                print_format() 
    return 0

def print_format():
    logging.info("="*55)

def run_caliper_tests(target):
    if os.path.exists(caliper_path.EXEC_LOG_DIR):
        shutil.rmtree(caliper_path.EXEC_LOG_DIR)
    os.mkdir(caliper_path.EXEC_LOG_DIR)
    if not os.path.exists(caliper_path.RESULTS_DIR):
        os.mkdir(caliper_path.RESULTS_DIR)
    if not os.path.exists(caliper_path.YAML_DIR):
        os.mkdir(caliper_path.YAML_DIR)
    if not os.path.exists(caliper_path.HTML_DIR):
        os.mkdir(caliper_path.HTML_DIR)
    
    flag = 0
    target_execution_dir = server_utils.get_target_exec_dir(target)
    if not os.path.exists(target_execution_dir):
        flag = 1
    try:
        logging.debug("beginnig to run the test cases")
        test_result = caliper_run(target_execution_dir, target)
    except error.CmdError, e:
        logging.info( "There is wrong in running benchmarks")
        flag = 1
    else:
        if test_result:
            flag = test_result 
    return flag

if __name__=="__main__":
    caliper_run(sys.argv[1])
