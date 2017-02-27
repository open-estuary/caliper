# wuyanjun w00291783
# wu.wu@hisilicon.com
# copyright

import os
import sys
import time
import shutil
import importlib
import types
import string
import re
import logging
import datetime
import subprocess
import socket
import yaml
try:
    import caliper.common as common
except ImportError:
    import common
#for ltp
from caliper.server.hosts import abstract_ssh
#import caliper.server.utils as server_utils
#for ltp
from caliper.server.parser_process import test_perf_tranver as traverse
from caliper.server import crash_handle
from caliper.client.shared import error
from caliper.server import utils as server_utils
from caliper.client.shared import utils
from caliper.client.shared import caliper_path
from caliper.client.shared.settings import settings
from caliper.server.run import write_results
from caliper.client.shared.caliper_path import folder_ope as Folder
from caliper.client.shared.caliper_path import intermediate


def get_server_command(kind_bench, section_name):
    server_config_file = ''

    server_config_file = server_utils.get_server_cfg_path(kind_bench)
    if server_config_file != '':
        server_config, server_sections = \
                server_utils.read_config_file(server_config_file)
        if section_name in server_sections:
            command = server_config.get(section_name, 'command')
            logging.debug("command is %s" % command)
            return command
        else:
            return None
    else:
        return None


def parse_all_cases(target_exec_dir, target, kind_bench, bench_name,
                     run_file,parser_file,dic):
    """
    function: run one benchmark which was selected in the configuration files
    """
    try:
        # get the abspath, which is filename of run config for the benchmark
        bench_conf_file = os.path.join(
                                    caliper_path.config_files.tests_cfg_dir,
                                    kind_bench, run_file)
        # get the config sections for the benchmrk
        configRun, sections_run = server_utils.read_config_file(
                                                    bench_conf_file)
    except AttributeError as e:
        raise AttributeError
    except Exception:
        raise
    bench_test = "ltp"
    logging.debug("the sections to run are: %s" % sections_run)
    if not os.path.exists(Folder.exec_dir):
        os.mkdir(Folder.exec_dir)
    log_bench = os.path.join(Folder.exec_dir, bench_name)
    logfile = log_bench + "_output.log"
    if bench_name != bench_test:
    	if not os.path.exists(logfile):
	    return -1
    tmp_log_file = log_bench + "_output_tmp.log"
    parser_result_file = log_bench + "_parser.log"
    tmp_parser_file = log_bench + "_parser_tmp.log"
    if os.path.exists(parser_result_file):
        os.remove(parser_result_file)
    #output_logs_names = glob.glob(Folder.exec_dir+"/*output.log")

    # for each command in run config file, read the config for the benchmark
    for i in range(0, len(sections_run)):
        dic[bench_name][sections_run[i]] = {}

        flag = 0
        try:
            category = configRun.get(sections_run[i], 'category')
            scores_way = configRun.get(sections_run[i], 'scores_way')
            parser = configRun.get(sections_run[i], 'parser')
            command = configRun.get(sections_run[i], 'command')
        except Exception:
            logging.debug("no value for the %s" % sections_run[i])
            continue
	if bench_name == bench_test:
	    subsection = sections_run[i].split(" ")[1]
	    subsection_file = log_bench + "_" + subsection + "_output.log"
            if not os.path.exists(subsection_file):
            	continue
        if os.path.exists(tmp_parser_file):
            os.remove(tmp_parser_file)
        # parser the result in the tmp_log_file, the result is the output of
        # running the command

        try:
            logging.debug("Parsering the result of command: %s" % command)
            if bench_name == bench_test:
                outfp = open(tmp_parser_file, "w")
                outfp.write("%s" %(subsection))
                outfp.close()
                parser_result = parser_case(kind_bench, bench_name, parser_file,
                                        parser, subsection_file,
                                        tmp_parser_file)
            else:
                outfp = open(logfile, 'r')
                infp = open(tmp_log_file, 'w')
                infp.write(re.findall("test start\s+%+(.*?)%+\s+test_end", outfp.read(), re.DOTALL)[i])
                infp.close()
                outfp.close()
                parser_result = parser_case(kind_bench, bench_name, parser_file,
                                        parser,tmp_log_file,
                                        tmp_parser_file)
            dic[bench_name][sections_run[i]]["type"] = type(parser_result)
            dic[bench_name][sections_run[i]]["value"] = parser_result
        except Exception, e:
            logging.info("Error while parsing the result of \" %s \""
                            % sections_run[i])
            logging.info(e)
            if os.path.exists(tmp_parser_file):
                os.remove(tmp_parser_file)
            if os.path.exists(tmp_log_file):
                os.remove(tmp_log_file)
        else:
            server_utils.file_copy(parser_result_file, tmp_parser_file, "a+")
            if os.path.exists(tmp_parser_file):
                os.remove(tmp_parser_file)
            if os.path.exists(tmp_log_file):
                os.remove(tmp_log_file)
            if (parser_result <= 0):
                continue

def compute_caliper_logs(target_exec_dir,flag = 1):
    # according the method in the config file, compute the score
    dic = yaml.load(open(caliper_path.folder_ope.final_parser, 'r'))
    config_files = server_utils.get_cases_def_files(target_exec_dir)
    for i in range(0, len(config_files)):
        config_file = os.path.join(config_files[i])
        config, sections = server_utils.read_config_file(config_file)
        classify = config_files[i].split("/")[-1].strip().split("_")[0]
        for j in range(0, len(sections)):
            try:
                run_file = config.get(sections[j], 'run')
                parser = config.get(sections[j], 'parser')
            except Exception:
                raise AttributeError("The is no option value of Computing")

            print_format()
            if flag == 1:
                logging.info("Generation raw yaml for %s" % sections[j])
            else:
                logging.info("Computing Score for %s" % sections[j])
            bench = os.path.join(classify, sections[j])
            try:
                # get the abspath, which is filename of run config for the benchmark
                bench_conf_file = os.path.join(
                                caliper_path.config_files.tests_cfg_dir,
                                bench, run_file)
                # get the config sections for the benchmrk
                configRun, sections_run = server_utils.read_config_file(
                                                    bench_conf_file)
            except AttributeError as e:
                raise AttributeError
            except Exception:
                raise
            for k in range(0, len(sections_run)):
                try:
                    category = configRun.get(sections_run[k], 'category')
                    scores_way = configRun.get(sections_run[k], 'scores_way')
                    command = configRun.get(sections_run[k], 'command')
                except Exception:
                    logging.debug("no value for the %s" % sections_run[k])
                    logging.info(e)
                    continue
                try:
                    logging.debug("Computing the score of the result of command: %s"
                                % command)
                    flag_compute = compute_case_score(dic[sections[j]][sections_run[k]]["value"], category,
                                          scores_way, target_exec_dir, flag)
                except Exception, e:
                    logging.info("Error while computing the result of \"%s\""  % sections_run[k])
                    logging.info(e)
                    continue
                else:
                    if not flag_compute and dic[bench][sections_run[k]["value"]]:
                            logging.info("Error while computing the result\
                                        of \"%s\"" % command)
    logging.info("="*55)
    if not os.path.exists(caliper_path.HTML_DATA_DIR_INPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_INPUT)

    if not os.path.exists(caliper_path.HTML_DATA_DIR_OUTPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_OUTPUT)

def run_all_cases(target_exec_dir, target, kind_bench, bench_name,
                    run_file):
    """
    function: run one benchmark which was selected in the configuration files
    """
    try:
        # get the abspath, which is filename of run config for the benchmark
        bench_conf_file = os.path.join(
                                    caliper_path.config_files.tests_cfg_dir,
                                    kind_bench, run_file)
        # get the config sections for the benchmrk
        configRun, sections_run = server_utils.read_config_file(
                                                    bench_conf_file)
    except AttributeError as e:
        raise AttributeError
    except Exception:
        raise
    logging.debug("the sections to run are: %s" % sections_run)
    if not os.path.exists(Folder.exec_dir):
        os.mkdir(Folder.exec_dir)
    log_bench = os.path.join(Folder.exec_dir, bench_name)
    logfile = log_bench + "_output.log"
    tmp_log_file = log_bench + "_output_tmp.log"
    if os.path.exists(logfile):
        os.remove(logfile)

    starttime = datetime.datetime.now()
    if os.path.exists(Folder.caliper_log_file):
        sections = bench_name + " EXECUTION"
        fp = open(Folder.caliper_log_file,"r")
        f = fp.readlines()
        fp.close()
        op = open(Folder.caliper_log_file,"w")
        for line in f:
            if not(sections in line):
                op.write(line)
        op.close()
    result = subprocess.call("echo '$$ %s EXECUTION START: %s' >> %s"
                            % (bench_name,
                                str(starttime)[:19],
                                Folder.caliper_log_file),
                            shell=True)
    bench_test = "ltp"
    if  bench_name == bench_test:
        tar_ip = settings.get_value('CLIENT', 'ip', type=str)
        target.run("if [[ ! -e /mnt/caliper_nfs ]]; then mkdir -p /mnt/caliper_nfs; fi")
# fix me , now that we create the folder, why not we mount it directly here
        try:
             tar_mask = ".".join(tar_ip.split(".")[0:3])
             p1 = subprocess.Popen(["ifconfig"], stdout=subprocess.PIPE)
             p2 = subprocess.Popen(["grep", tar_mask], stdin=p1.stdout, stdout=subprocess.PIPE)
             p1.stdout.close()
             output,err = p2.communicate()
             output = output.strip()
             host_ip = output.split("inet addr:")[1].split(" ")[0]
        except Exception:
            logging.debug("Unable to get the host_ip" )
        try:
            mount_cmd = target.run("mount -t nfs %s:/opt/caliper_nfs /mnt/caliper_nfs" % (host_ip) )
        except Exception:
            try:
                umount_cmd = target.run("umount /mnt/caliper_nfs/")
                mount_cmd = target.run("mount -t nfs %s:/opt/caliper_nfs /mnt/caliper_nfs" % (host_ip) )
            except Exception:
                logging.debug("Unable to mount")
                return result
        readme_file=log_bench+"_README"
        resultltp = subprocess.call("touch %s"
                             %(readme_file),shell=True)
        resultltp = subprocess.call("echo 'The categorization of ltp in caliper is\nCATEGORY\t\t\t\t\t\tSCENARIOS OF LTP\n\n[command]\t\t\t\t\t\tcommands\n[cpu]\t\t\t\t\t\tsched,cpuhotplug\n[memory]\t\t\t\t\t\tmm.numa,hugetlb\n[dio]\t\t\t\t\t\tdio,io,dma_thread_diotest,timers\n[filesystem]\t\t\t\t\t\tfilecaps,fs,fs_bind,fs_ext4,fs_perms_simple,fs_readonly\n[kernel/\t\t\t\t\t\tsyscalls,controllers,pty,containers,admin_tools,modules,can\n[proc]\t\t\t\t\t\tipc,hyperthreading,nptl,cap_bounds,connectors,pipes\n\n\nltp_output.log contains the screenshot of complete ltp execution and ltp_parser.log contains the information regarding the number of tests executed and among them which all have passed failed or skipped.\n\nFor more information regarding a particular category please see ltp_<category>_output.log which contains the output screen and parser log for that particular category' >> %s"
                  %(readme_file),shell=True)
    # for each command in run config file, read the config for the benchmark
    for i in range(0, len(sections_run)):
        flag = 0
        try:
            category = configRun.get(sections_run[i], 'category')
            command = configRun.get(sections_run[i], 'command')
        except Exception:
            logging.debug("no value for the %s" % sections_run[i])
            continue
	if bench_name == bench_test:
	    subsection = sections_run[i].split(" ")[1]
	    subsection_file = log_bench + "_" + subsection + "_output.log"
        if os.path.exists(tmp_log_file):
            os.remove(tmp_log_file)

        server_run_command = get_server_command(kind_bench, sections_run[i])
        logging.debug("Get the server command is: %s" % server_run_command)
        # run the command of the benchmarks
        try:
            flag = run_kinds_commands(sections_run[i], server_run_command,
                                      tmp_log_file, kind_bench,
                                      target, command)
        except Exception, e:
            logging.info(e)
            crash_handle.main()
            if bench_name == bench_test:
                 move_logs = subprocess.call("cp /opt/caliper_nfs/ltp_log/* %s "
                                % (Folder.exec_dir), shell=True)
            server_utils.file_copy(logfile, tmp_log_file, 'a+')
            if os.path.exists(tmp_log_file):
                os.remove(tmp_log_file)
            run_flag = server_utils.get_fault_tolerance_config(
                                'fault_tolerance', 'run_error_continue')
            if run_flag == 1:
              continue
            else:
              return result
        else:
            if bench_name == bench_test:
                move_logs = subprocess.call("cp /opt/caliper_nfs/ltp_log/* %s "
                                % (Folder.exec_dir), shell=True)
                if os.path.exists(subsection_file):
                    server_utils.file_copy(tmp_log_file,subsection_file, 'a+')
            server_utils.file_copy(logfile, tmp_log_file, 'a+')
            if flag != 1:
                logging.info("There is wrong when running the command \"%s\""
                                % command)
                if os.path.exists(tmp_log_file):
                    os.remove(tmp_log_file)
                crash_handle.main()

                run_flag = server_utils.get_fault_tolerance_config(
                                'fault_tolerance', 'run_error_continue')
                if run_flag == 1:
                    if bench_name != bench_test:
                       continue
                else:
                    return result
            if os.path.exists(tmp_log_file):
                os.remove(tmp_log_file)

    endtime = datetime.datetime.now()
    result = subprocess.call("echo '$$ %s EXECUTION STOP: %s' >> %s"
                                % (sections_run[i], str(endtime)[:19],
                                    Folder.caliper_log_file), shell=True)
    result = subprocess.call("echo '$$ %s EXECUTION DURATION %s Seconds'>>%s"
                                % (sections_run[i],
                                    (endtime-starttime).seconds,
                                    Folder.caliper_log_file), shell=True)

def run_commands(exec_dir, kind_bench, commands,
                    stdout_tee=None, stderr_tee=None, target=None):
    returncode = -1
    output = ''

    if not os.path.exists(exec_dir):
    	output = exec_dir + ' not exist'
    	return [output, returncode]

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
        logging.debug(e)
    else:
        if result.exit_status and result.stderr and not result.stdout:
            returncode = result.exit_status
        else:
            returncode = 0
        try:
            output = result.stdout
        except Exception:
            output = result.stderr
    os.chdir(pwd)
    return [output, returncode]


# normalize the commands
def get_actual_commands(commands, target):
    if commands is None or commands == '':
        return None
    post_commands = commands

    if re.findall('\$SERVER_IP', commands):
        try:
            server_ip = settings.get_value('SERVER', 'ip', type=str)
        except Exception, e:
            server_ips = server_utils.get_local_ip()
            server_ip = ""

            for each_ip in server_ips:
                items = each_ip.split(".")[0:2]
                pre = '.'.join(items)
                if target.ip.startswith(pre):
                    server_ip = each_ip
                    break
            if not server_ip:
                if len(server_ips) > 1:
                    try:
                        server_ips.remove("127.0.0.1")
                    except Exception:
                        raise e

                server_ip = server_ips[0]
        strinfo = re.compile('\$SERVER_IP')
        post_commands = strinfo.sub(server_ip, commands)
    commands = post_commands

    if re.findall('\$CLIENT_IP', commands):
        try:
            client_ip = settings.get_value('CLIENT', 'ip', type=str)
        except Exception, e:
            client_ip = '127.0.0.1'
        strinfo = re.compile('\$CLIENT_IP')
        post_commands = strinfo.sub(client_ip, commands)

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
            logging.debug("the actual commands running on the remote host "
                            "is: %s" % final_commands)
            result = target.run(final_commands, stdout_tee=stdout_tee,
                                stderr_tee=stderr_tee, verbose=True)
        else:
            return ['Not command specified', -1]
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    except Exception, e:
        logging.debug(e)
    else:
        if result.exit_status and result.stderr and not result.stdout:
            returncode = result.exit_status
        else:
            returncode = 0
        try:
            output = result.stdout
        except Exception:
            output = result.stderr
    return [output, returncode]


def run_client_command(cmd_sec_name, tmp_logfile, kind_bench,
                        target, command):
    fp = open(tmp_logfile, "a+")
    start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd_sec_name
    fp.write(start_log)
    fp.write("<<<BEGIN TEST>>>\n")
    tags = "[test: " + cmd_sec_name + "]\n"
    fp.write(tags)
    logs = "log: " + get_actual_commands(command, target) + "\n"
    fp.write(logs)
    start = time.time()
    flag = 0
    logging.debug("the client running command is %s" % command)

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
        host_exec_dir = os.path.join(host_current_pwd, 'caliper',
                                        "binary", arch)

    try:
        logging.debug("begining to execute the command of %s on remote host"
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
        fp.write("[status]: FAIL\n")
        sys.stdout.write(e)
        flag = -1
    else:
        if not returncode:
            fp.write("[status]: PASS\n")
            flag = 1
        else:
            fp.write("[status]: FAIL\n")
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
        logging.info(e)
    else:
        os._exit(return_code)


def run_case(cmd_sec_name, server_command, tmp_logfile, kind_bench,
                target, command):
    if server_command is None or server_command == '':
        return
    if command is None or command == '':
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
                                                  kind_bench, target, command)
            except Exception, e:
                logging.info("There is wrong with running the remote host\
                                command of %s" % command)
                logging.debug(e.args[0], e.args[1])
                utils.kill_process_tree(newpid)
            else:
                utils.kill_process_tree(newpid)
                return return_code
    return 0


def run_kinds_commands(cmd_sec_name, server_run_command, tmp_logfile,
                        kind_bench, target, command):
    if server_run_command != '' and server_run_command is not None:
        logging.debug("Running the server_command: %s, "
                        "and the client command: %s" %
                        (server_run_command, command))
        flag = run_case(cmd_sec_name, server_run_command, tmp_logfile,
                        kind_bench, target, command)
    else:
        logging.debug("only running the command %s in the remote host"
                        % command)
        flag = run_client_command(cmd_sec_name, tmp_logfile, kind_bench,
                                    target, command)
    return flag


def parser_case(kind_bench, bench_name, parser_file, parser, infile, outfile):
    if not os.path.exists(infile):
        return -1
    result = 0
    fp = open(outfile, 'a+')
    # the parser function defined in the config file is to filter the output.
    # get the abspth of the parser.py which is defined in the config files.
    # changed by Elaine Aug 8-10
    if not parser_file:
        pwd_file = bench_name + "_parser.py"
        parser_file = os.path.join(caliper_path.PARSER_DIR, pwd_file)
    else:
        parser_file = os.path.join(caliper_path.PARSER_DIR, parser_file)
    rel_path = os.path.relpath(parser_file,
            os.path.dirname(caliper_path.CALIPER_DIR))
    parser_path = rel_path.split(".")[0]
    parser_name = parser_path.replace(os.sep, '.')

    result = 0
    if os.path.isfile(parser_file):
        try:
            # import the parser module import_module
            parser_module = importlib.import_module(parser_name)
        except ImportError, e:
            logging.info(e)
            return -3
        try:
            methodToCall = getattr(parser_module, parser)
        except Exception, e:
            logging.info(e)
            return -4
        else:
            infp = open(infile, "r")
            outfp = open(outfile, 'a+')
            contents = infp.read()

	    if  bench_name == "ltp":
                 result = methodToCall(contents, outfp)
	    else:

              for content in re.findall("BEGIN TEST(.*?)\[status\]", contents,
                                        re.DOTALL):
                try:
                    # call the parser function to filter the output
                    logging.debug("Begining to parser the result of the case")
                    result = methodToCall(content, outfp)
                except Exception, e:
                    logging.info(e)
                    return -5
            outfp.close()
            infp.close()
    fp.close()
    return result


def compute_case_score(result, category, score_way, target, flag):
    tmp = category.split()
    length = len(tmp)
    # write the result and the corresponding score to files
    target_name = server_utils.get_host_name(target)
    yaml_dir = os.path.join(Folder.results_dir, 'yaml')
    result_yaml_name = target_name + '.yaml'
    score_yaml_name = target_name + '_score.yaml'
    if flag == 1:
        result_yaml = os.path.join(yaml_dir, result_yaml_name)
    else :
        result_yaml = os.path.join(yaml_dir, score_yaml_name)
    if (length == 4 and tmp[0] == 'Functional'):
        return compute_func(result, tmp, score_way, result_yaml, flag)
    elif ((length != 0 and length <= 4) and tmp[0] == 'Performance'):
        return compute_perf(result, tmp, score_way, result_yaml, flag)
    else:
        return -4


def compute_func(result, tmp, score_way, result_yaml, flag=1):
    flag1 = 0
    if flag == 2:
        result = result * 100
    try:
        flag1 = write_results.write_yaml_func(result_yaml,
                                                tmp, result,
                                                flag)
    except BaseException:
        logging.debug("There is wrong when computing the score")
    return flag1


def compute_perf(result, tmp, score_way, result_yaml, flag=1):
    result_flag = 1
    score_flag = 2

    if type(result) is types.StringType:
        if re.search('\+', result):
            result = result.replace('\+', 'e')
        result_fp = string.atof(result)
    elif type(result) is types.FloatType:
        result_fp = result
    elif type(result) is types.IntType:
        result_fp = result
    elif (type(result) == dict and (len(tmp) > 0 and len(tmp) < 4)):
        return deal_dic_for_yaml(result, tmp, score_way,
                                    result_yaml,flag)
    else:
        return -4

    if flag == 2:
        result_fp = write_results.compute_score(score_way, result_fp)
    flag1 = 0
    try:
        flag1 = write_results.write_yaml_perf(result_yaml, tmp,
                                                result_fp, flag)
    except BaseException:
        logging.debug("There is wrong when compute the score.")
    return flag1


def deal_dic_for_yaml(result, tmp, score_way, yaml_file,flag):
    if (len(tmp) == 2):
        status = write_results.write_dic(result, tmp, score_way,
                                yaml_file, flag)
    elif (len(tmp) == 3):
        status = write_results.write_sin_dic(result, tmp, score_way, yaml_file, flag)
    else:
        status = write_results.write_multi_dic(result, tmp, score_way,
                                            yaml_file, flag)
    return status

def system_initialise(target):
    target.run(" sync; echo 3 > /proc/sys/vm/drop_caches; swapoff -a && swapon -a ")


def caliper_run(target_exec_dir, server,target):
    # get the test cases defined files
    config_files = server_utils.get_cases_def_files(target_exec_dir)
    logging.debug("the selected configuration are %s" % config_files)

    for i in range(0, len(config_files)):
        # run benchmarks selected in each configuration file
        # config_file = os.path.join(caliper_path.CALIPER_PRE, config_files[i])
        config_file = os.path.join(config_files[i])
        config, sections = server_utils.read_config_file(config_file)
        logging.debug(sections)

        # get if it is the 'common' or 'arm' or 'android'
        classify = config_files[i].split("/")[-1].strip().split("_")[0]
        logging.debug(classify)

	if classify == "server" and server:
            try:
	    	server_ip = settings.get_value("SERVER","ip",type=str)
	    	server_port = settings.get_value("SERVER","port",type=int)
                server_user = settings.get_value("SERVER","user",type=str)
                logging.info("Please wait while caliper triggers the server.py script in the server")
                server_pwd = server.run("pwd").stdout
                server_pwd = server_pwd.split("\n")[0]
                server_caliper_dir = os.path.join(server_pwd, "caliper_server")
                server_caliper_dir = os.path.join(server_caliper_dir,"server.py")
                server_user = server_user + '@' + server_ip
                script = server_caliper_dir + ' ' + str(server_port)
                subprocess.Popen(['ssh', '%s' % server_user, 'python %s' % script])


	    except Exception as e:
		logging.info(e)
		raise AttributeError("Error in establising connection with server")

        for i in range(0, len(sections)):
            # run for each benchmark
            target_arch = server_utils.get_host_arch(target)
            build_name = sections[i]+'_'+target_arch+'.suc'
            build_suc = os.path.join(Folder.build_dir, build_name)
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
                system_initialise(target)
		if classify == "server":
                    logging.info("Waiting for server to grant access")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  		    sock.connect((server_ip,server_port))
		    logging.info("%s" % str(sock.recv(1024)))

                result = run_all_cases(target_exec_dir, target, bench,
                                        sections[i], run_file)
		if classify == "server":
		    sock.send("1")
		    sock.close()
            except Exception:
                logging.info("Running %s Exception" % sections[i])
                crash_handle.main()
                print_format()
                if sections[i]== "ltp":
                    try:
                        unmount = target.run("if  df -h |grep caliper_nfs  ; then umount /mnt/caliper_nfs/; fi")
                    except Exception:
                        unmount = target.run("if  df -h |grep caliper_nfs  ; then fuser -km /mnt/caliper_nfs ;fi")
                        unmount = target.run("if  df -h |grep caliper_nfs  ; then umount /mnt/caliper_nfs/ ;fi")
                run_flag = server_utils.get_fault_tolerance_config(
                                'fault_tolerance', 'run_error_continue')
                if run_flag == 1:
                    continue
                else:
                    return result
            else:
                logging.info("Running %s Finished" % sections[i])
                if sections[i] == "ltp":
                    try:
                         unmount = target.run("if  df -h |grep caliper_nfs  ; then umount /mnt/caliper_nfs/ ;fi")
                    except Exception:
                         unmount = target.run("if  df -h |grep caliper_nfs  ; then fuser -km /mnt/caliper_nfs/ ;fi")
                         unmount = target.run("if  df -h |grep caliper_nfs  ; then umount /mnt/caliper_nfs/ ;fi")
                print_format()

    return 0


def parsing_run(target_exec_dir, target):
    # get the test cases defined files
    config_files = server_utils.get_cases_def_files(target_exec_dir)
    logging.debug("the selected configuration are %s" % config_files)
    dic = {}
    for i in range(0, len(config_files)):
        # run benchmarks selected in each configuration file
        # config_file = os.path.join(caliper_path.CALIPER_PRE, config_files[i])
        config_file = os.path.join(config_files[i])
        config, sections = server_utils.read_config_file(config_file)
        logging.debug(sections)

        # get if it is the 'common' or 'arm' or 'android'
        classify = config_files[i].split("/")[-1].strip().split("_")[0]
        logging.debug(classify)

        for i in range(0, len(sections)):
            dic[sections[i]] = {}
            # try to resolve the configuration of the configuration file
            try:
                run_file = config.get(sections[i], 'run')
                parser = config.get(sections[i], 'parser')
            except Exception:
                raise AttributeError("The is no option value of parser")

            print_format()
            logging.info("Parsing %s" % sections[i])
            bench = os.path.join(classify, sections[i])

            try:
                result = parse_all_cases(target_exec_dir, target, bench,
                                       sections[i], run_file,parser,dic)
            except Exception:
                logging.info("Running %s Exception" % sections[i])
                crash_handle.main()
                print_format()
                run_flag = server_utils.get_fault_tolerance_config(
                    'fault_tolerance', 'run_error_continue')
                if run_flag == 1:
                    continue
                else:
                    return result
            else:
                logging.info("Parsing %s Finished" % sections[i])
                print_format()
    outfp = open(os.path.join(caliper_path.folder_ope.workspace,
                              caliper_path.folder_ope.name.strip()
                              +"/final_parsing_logs.yaml"),'w')
    outfp.write(yaml.dump(dic, default_flow_style=False))
    outfp.close()
    return 0

def print_format():
    logging.info("="*55)


def run_caliper_tests(target,server,f_option):
    #f_option =1 if -f is used
    if f_option == 1:
        if not os.path.exists(Folder.exec_dir):
            os.mkdir(Folder.exec_dir)
    else:
        if os.path.exists(Folder.exec_dir):
            shutil.rmtree(Folder.exec_dir)
        os.mkdir(Folder.exec_dir)
    if not os.path.exists(Folder.results_dir):
        os.mkdir(Folder.results_dir)
    if not os.path.exists(Folder.yaml_dir):
        os.mkdir(Folder.yaml_dir)
    if not os.path.exists(Folder.html_dir):
        os.mkdir(Folder.html_dir)

    flag = 0
    target_execution_dir = server_utils.get_target_exec_dir(target)
    if not os.path.exists(target_execution_dir):
        flag = 1
    try:
        logging.debug("beginnig to run the test cases")
        test_result = caliper_run(target_execution_dir,server, target)
        if intermediate == 1:
            target_name = server_utils.get_host_name(target)
            yaml_dir = os.path.join(Folder.results_dir, 'yaml')
            result_yaml_name = target_name + '.yaml'
            result_yaml = os.path.join(yaml_dir, result_yaml_name)
            dic = {}
            dic = traverse.traverse_pre(target, dic)
            with open(result_yaml,'w') as fp:
                fp.write(yaml.dump(dic, default_flow_style=False))

    except error.CmdError:
        logging.info("There is wrong in running benchmarks")
        flag = 1
    else:
        if test_result:
            flag = test_result
    return flag

def parser_caliper_tests(target,f_option):
    #f_option =1 if -f is used
    if not os.path.exists(Folder.exec_dir):
            print "Invalid Parser input Folder"
            return -1

    if not os.path.exists(Folder.results_dir):
        os.mkdir(Folder.results_dir)
    if not os.path.exists(Folder.yaml_dir):
        os.mkdir(Folder.yaml_dir)
    if not os.path.exists(Folder.html_dir):
        os.mkdir(Folder.html_dir)
    flag = 0
    target_execution_dir = server_utils.get_target_exec_dir(target)
    try:
        logging.debug("beginnig to parse the test cases")
        test_result = parsing_run(target_execution_dir, target)
    except error.CmdError:
        logging.info("There is wrong in parsing test cases")
        flag = 1
    else:
        if test_result:
            flag = test_result
    return flag

if __name__ == "__main__":
    caliper_run(sys.argv[1])
