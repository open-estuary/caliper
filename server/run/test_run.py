#!/usr/bin/env python

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
import threading
import json
try:
    import caliper.common as common
except ImportError:
    import common
# for ltp
from caliper.server.hosts import abstract_ssh
# import caliper.server.utils as server_utils
# for ltp
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


class myThread(threading.Thread):
    def __init__(self, threadID, cmd_sec_name, server_run_command, tmp_logfile,
                 kind_bench, server):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.cmd_sec_name = cmd_sec_name
        self.server_run_command = server_run_command
        self.tmp_logfile = tmp_logfile
        self.kind_bench = kind_bench
        self.server = server

    def run(self):
        client_thread_func(self.cmd_sec_name, self.server_run_command, self.tmp_logfile,
                           self.kind_bench, self.server)


def get_server_command(kind_bench, section_name):
    server_config_file = ''

    server_config_file = server_utils.get_server_cfg_path(kind_bench)
    if server_config_file != '':
        server_config, server_sections = \
            server_utils.read_config_file(server_config_file)
        if section_name in server_sections:
            try:
                command = server_config.get(section_name, 'command')
                logging.debug("command is %s" % command)
                return command
            except:
                return None
        else:
            return None
    else:
        return None


def get_nginx_client_command(kind_bench, section_name, command_field):
    application_config_file = ''

    application_config_file = server_utils.get_application_cfg_path(kind_bench)
    if application_config_file != '':
        server_config, server_sections = \
            server_utils.read_config_file(application_config_file)
        if section_name in server_sections:
            try:
                command = server_config.get(section_name, command_field)
                logging.debug("command is %s" % command)
                return command
            except:
                return None
        else:
            return None
    else:
        return None


def parse_all_cases(kind_bench, bench_name, parser_file, dic):
    """
    function: parse one benchmark which was selected in the configuration files
    """
    try:
        # get the abspath, which is filename of run config for the benchmark
        # get the config sections for the benchmrk
        bench_conf_file = os.path.join(kind_bench, 'main.yml')
        # get the config sections for the benchmrk
        pf = open(bench_conf_file, 'r')
        values = yaml.load(pf.read())
        sections_run = values[bench_name].keys()
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
    # output_logs_names = glob.glob(Folder.exec_dir+"/*output.log")

    # for each command in run config file, read the config for the benchmark
    for i in range(0, len(sections_run)):
        dic[bench_name][sections_run[i]] = {}

        flag = 0
        try:
            parser = values[bench_name][sections_run[i]]['parser']
            command = values[bench_name][sections_run[i]]['command']
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
            outfp = open(logfile, 'r')
            infp = open(tmp_log_file, 'w')
            infp.write(re.findall("test start\s+%+(.*?)%+\s+test_end", outfp.read(), re.DOTALL)[i])
            infp.close()
            outfp.close()
            parser_result = parser_case(bench_name, parser_file,
                                        parser, tmp_log_file,
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


def compute_caliper_logs(target_exec_dir, flag=1):
    # according the method in the config file, compute the score
    dic = yaml.load(open(caliper_path.folder_ope.final_parser, 'r'))
    config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
    fp = open(config_files, 'r')
    tool_list = []
    case_list = yaml.load(fp.read())
    for dimension in case_list:
        for i in range(len(case_list[dimension])):
            for tool in case_list[dimension][i]:
                for case in case_list[dimension][i][tool]:
                    if case_list[dimension][i][tool][case][0] == 'enable':
                        tool_list.append(tool)
    sections = list(set(tool_list))
    for j in range(0, len(sections)):
        try:
            run_file = sections[j] + '_run.cfg'
            parser = sections[j] + '_parser.py'
        except Exception:
            raise AttributeError("The is no option value of Computing")

        print_format()
        if flag == 1:
            logging.info("Generation raw yaml for %s" % sections[j])
            bench = os.path.join(caliper_path.BENCHS_DIR, sections[j], 'defaults')
        else:
            logging.info("Computing Score for %s" % sections[j])
            bench = os.path.join(caliper_path.BENCHS_DIR, sections[j], 'defaults')
        try:
            # get the abspath, which is filename of run config for the benchmark
            bench_conf_file = os.path.join(bench, 'main.yml')
            # get the config sections for the benchmrk
            pf = open(bench_conf_file, 'r')
            values = yaml.load(pf.read())
            sections_run = values[sections[j]].keys()
        except AttributeError as e:
            raise AttributeError
        except Exception:
            raise
        for k in range(0, len(sections_run)):
            try:
                category = values[sections[j]][sections_run[k]]['category']
                scores_way = values[sections[j]][sections_run[k]]['scores_way']
                command = values[sections[j]][sections_run[k]]['command']
            except Exception, e:
                logging.debug("no value for the %s" % sections_run[k])
                logging.info(e)
                continue
            try:
                logging.debug("Computing the score of the result of command: %s"
                              % command)
                flag_compute = compute_case_score(dic[sections[j]][sections_run[k]]["value"], category,
                                                  scores_way, target_exec_dir, flag)
            except Exception, e:
                logging.info("Error while computing the result of \"%s\"" % sections_run[k])
                logging.info(e)
                continue
            else:
                if not flag_compute and dic[bench][sections_run[k]["value"]]:
                    logging.info("Error while computing the result\
                                    of \"%s\"" % command)
    logging.info("=" * 55)
    if not os.path.exists(caliper_path.HTML_DATA_DIR_INPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_INPUT)

    if not os.path.exists(caliper_path.HTML_DATA_DIR_OUTPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_OUTPUT)


def run_all_cases(kind_bench, bench_name):
    """
    function: run one benchmark which was selected in the configuration files
    """
    try:
        # get the abspath, which is filename of run config for the benchmark
        bench_conf_file = os.path.join(kind_bench, 'main.yml')
        # get the config sections for the benchmrk
        pf = open(bench_conf_file, 'r')
        values = yaml.load(pf.read())
        sections_run = values[bench_name].keys()
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

    nginx_tmp_log_file = None

    starttime = datetime.datetime.now()
    if os.path.exists(Folder.caliper_log_file):
        sections = bench_name + " EXECUTION"
        fp = open(Folder.caliper_log_file, "r")
        f = fp.readlines()
        fp.close()
        op = open(Folder.caliper_log_file, "w")
        for line in f:
            if not (sections in line):
                op.write(line)
        op.close()
    result = subprocess.call("echo '$$ %s EXECUTION START: %s' >> %s"
                             % (bench_name,
                                str(starttime)[:19],
                                Folder.caliper_log_file),
                             shell=True)
    subprocess.call("echo '$$ %s RUN START: %s' >> %s"
                    % (bench_name,
                       str(starttime)[:19],
                       Folder.caliper_run_log_file),
                    shell=True)
    # for each command in run config file, read the config for the benchmark
    for i in range(0, len(sections_run)):
        flag = 0
        try:
            command = values[bench_name][sections_run[i]]['command']
        except Exception:
            logging.debug("no value for the %s" % sections_run[i])
            continue

        if os.path.exists(tmp_log_file):
            os.remove(tmp_log_file)

        # run the command of the benchmarks
        try:
            flag = run_client_command(sections_run[i], tmp_log_file, command, bench_name)
        except Exception, e:
            logging.info(e)
            crash_handle.main()
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
                    return result
            if os.path.exists(tmp_log_file):
                os.remove(tmp_log_file)

    endtime = datetime.datetime.now()
    subprocess.call("echo '$$ %s EXECUTION STOP: %s' >> %s"
                             % (sections_run[i], str(endtime)[:19],
                                Folder.caliper_log_file), shell=True)
    subprocess.call("echo '$$ %s EXECUTION DURATION %s Seconds'>>%s"
                             % (sections_run[i],
                                (endtime - starttime).seconds,
                                Folder.caliper_log_file), shell=True)

    subprocess.call("echo '$$ %s RUN STOP: %s' >> %s"
                             % (sections_run[i], str(endtime)[:19],
                                Folder.caliper_run_log_file), shell=True)
    subprocess.call("echo '$$ %s RUN DURATION %s Seconds'>>%s"
                             % (sections_run[i],
                                (endtime - starttime).seconds,
                                Folder.caliper_run_log_file), shell=True)
    subprocess.call("echo '======================================================'>>%s"% (Folder.caliper_run_log_file), shell=True)


# normalize the commands
def get_actual_commands(commands):
    if commands is None or commands == '':
        return None
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
    actual_commands = get_actual_commands(commands)
    final_commands = "cd %s; %s" % (exec_dir, actual_commands)
    return final_commands


def run_remote_server_commands(commands, server,
                               stdout_tee=None, stderr_tee=None, timeout=None):
    returncode = -1
    output = ''
    try:
        result = server.run(commands, stdout_tee=stdout_tee,
                            stderr_tee=stderr_tee, timeout=timeout, verbose=True)
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    except Exception, e:
        logging.debug(e)
    else:
        if result:
            returncode = result
        else:
            returncode = 0
        try:
            output = result
        except Exception:
            output = result
    return [output, returncode]


def run_server_command(cmd_sec_name, commands, tmp_logfile, kind_bench, server, timeout=None):
    fp = open(tmp_logfile, "a+")
    # tmp_logfile
    if not re.search('server', kind_bench):
        start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd_sec_name
        fp.write(start_log)
        fp.write("<<<BEGIN TEST>>>\n")
        tags = "[test: " + cmd_sec_name + "]\n"
        fp.write(tags)
        logs = "log: " + get_actual_commands(commands) + "\n"
        fp.write(logs)
    flag = 0
    start = time.time()

    returncode = -1
    output = ''

    try:
        # the commands is multiple lines, and was included by Quotation
        final_commands = get_actual_commands(commands)
        if final_commands is not None and final_commands != '':
            logging.debug("the actual commands running on the remote client is: %s" % final_commands)
            [out, returncode] = run_remote_server_commands(final_commands, server, fp, fp, timeout)
        else:
            return ['Not command specified', -1]
    except error.ServRunError, e:
        if not re.search('server', kind_bench):
            fp.write("[status]: FAIL\n")
        sys.stdout.write(e)
        flag = -1
    else:
        if not returncode:
            if not re.search('server', kind_bench):
                fp.write("[status]: PASS\n")
            flag = 1
        else:
            if not re.search('server', kind_bench):
                fp.write("[status]: FAIL\n")
            flag = 0

    end = time.time()
    interval = end - start
    fp.write("Time in Seconds: %.3fs\n" % interval)

    if not re.search('server', kind_bench):
        fp.write("<<<END>>>\n")
        fp.write("%%%%%% test_end %%%%%%\n\n")
    fp.close()
    return flag


def run_remote_client_commands(exec_dir, kind_bench, commands, target,
                               stdout_tee=None, stderr_tee=None):
    returncode = -1
    output = ''
    try:
        # the commands is multiple lines, and was included by Quotation
        final_commands = remote_commands_deal(commands, exec_dir, target)
        if final_commands is not None and final_commands != '':
            logging.debug("the actual commands running on the remote target"
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
        if result and result and not result:
            returncode = result
        else:
            returncode = 0
        try:
            output = result
        except Exception:
            output = result
    return [output, returncode]


def run_commands(bench_name, commands):
    returncode = -1
    output = ''

    pwd = os.getcwd()
    TEST_CASE_DIR = caliper_path.config_files.config_dir
    try:
        # the commands is multiple lines, and was included by Quotation
        actual_commands = get_actual_commands(commands)
        try:
            logging.debug("the actual commands running in local is: %s"
                          % actual_commands)
            test_case_dir = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'tests')
            os.chdir(test_case_dir)
            result = subprocess.call(
                'ansible-playbook -i %s/hosts %s.yml -u root>> %s 2>&1' % (
                    TEST_CASE_DIR, actual_commands, Folder.caliper_run_log_file), stdout=subprocess.PIPE, shell=True)
            # result = os.system(actual_commands)
        except error.CmdError, e:
            raise error.ServRunError(e.args[0], e.args[1])
    except Exception, e:
        logging.debug(e)
    else:
        if result:
            returncode = result
        else:
            returncode = 0
        try:
            output = result
        except Exception:
            output = result
    os.chdir(pwd)
    return [output, returncode]


def run_client_command(cmd_sec_name, tmp_logfile, command, bench_name):
    fp = open(tmp_logfile, "a+")
    start_log = "%%%%%%         %s test start       %%%%%% \n" % cmd_sec_name
    fp.write(start_log)
    fp.write("<<<BEGIN TEST>>>\n")
    tags = "[test: " + cmd_sec_name + "]\n"
    fp.write(tags)
    logs = "log: " + get_actual_commands(command) + "\n"
    fp.write(logs)
    fp.close()
    start = time.time()
    flag = 0
    logging.debug("the client running command is %s" % command)

    try:
        logging.debug("begining to execute the command of %s on remote host"
                      % command)
        fp = open(tmp_logfile, "a+")
        logging.debug("client command in localhost is: %s" % command)
        # FIXME: update code for this condition
        [out, returncode] = run_commands(bench_name, command)
        fp.close()
        server_utils.file_copy(tmp_logfile, '/tmp/%s_output.log' % bench_name, 'a+')
    except error.ServRunError, e:
        fp = open(tmp_logfile, "a+")
        fp.write("[status]: FAIL\n")
        sys.stdout.write(e)
        flag = -1
        fp.close()
    else:
        fp = open(tmp_logfile, "a+")
        if not returncode:
            fp.write("[status]: PASS\n")
            flag = 1
        else:
            fp.write("[status]: FAIL\n")
            flag = 0
        fp.close()
    fp = open(tmp_logfile, "a+")
    end = time.time()
    interval = end - start
    fp.write("Time in Seconds: %.3fs\n" % interval)
    if not re.search('redis', bench_name):
        fp.write("<<<END>>>\n")
        fp.write("%%%%%% test_end %%%%%%\n\n")
    fp.close()
    return flag


def client_thread_func(cmd_sec_name, server_run_command, tmp_logfile,
                       kind_bench, server):
    flag = run_server_command(cmd_sec_name, server_run_command, tmp_logfile,
                              kind_bench, server, 5000)


def get_weighttp_process_count(host_login):
    p1 = subprocess.Popen(['ssh', '%s' % host_login, 'ps', '-ef'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', '-c', 'run_weighttp_script.sh'], stdin=p1.stdout, stdout=subprocess.PIPE)
    data = p2.communicate()
    data = str(data[0]).split("\n")
    return data[0]

def parser_case(bench_name, parser_file, parser, infile, outfile):
    if not os.path.exists(infile):
        return -1
    result = 0
    fp = open(outfile, 'a+')
    # the parser function defined in the config file is to filter the output.
    # get the abspth of the parser.py which is defined in the config files.
    # changed by Elaine Aug 8-10
    if not parser_file:
        pwd_file = bench_name + "_parser.py"
        parser_file = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers', pwd_file)
    else:
        parser_file = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers', parser_file)
    rel_path = bench_name + "_parser.py"
    parser_name = rel_path.replace('.py', '')
    handlers_path = os.path.join(caliper_path.BENCHS_DIR, bench_name, 'handlers')
    sys.path.append(handlers_path)

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

            if bench_name == "ltp":
                result = methodToCall(contents, outfp)
            elif bench_name == "nginx":
                try:
                    # call the parser function to filter the output
                    logging.debug("Begining to parser the result of the case")
                    result = methodToCall(contents, outfp)
                except Exception, e:
                    logging.info(e)
                    return -5
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
    else:
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
                                 result_yaml, flag)
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


def deal_dic_for_yaml(result, tmp, score_way, yaml_file, flag):
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


def caliper_run():
    # get the test cases defined files
    # config_files = server_utils.get_cases_def_files(target_exec_dir)
    # logging.debug("the selected configuration are %s" % config_files)
    config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
    fp = open(config_files, 'r')
    tool_list = []
    case_list = yaml.load(fp.read())
    for dimension in case_list:
        for i in range(len(case_list[dimension])):
            for tool in case_list[dimension][i]:
                for case in case_list[dimension][i][tool]:
                    if case_list[dimension][i][tool][case][0] == 'enable':
                        tool_list.append(tool)
    sections = list(set(tool_list))

    for i in range(0, len(sections)):
        # try to resolve the configuration of the configuration file
        try:
            run_file = sections[i]+ '_run.cfg'
            parser = sections[i]+ '_parser.py'
        except Exception:
            raise AttributeError("The is no option value of parser")

        print_format()

        logging.info("Running %s" % sections[i])
        bench = os.path.join(caliper_path.BENCHS_DIR, sections[i], 'defaults')
        try:
            # On some platforms, swapoff and swapon command is not able to execute.
            # So this function has been commented
            result = run_all_cases(bench, sections[i])
        except Exception, e:
            logging.info(e)
            logging.info("Running %s Exception" % sections[i])
            crash_handle.main()
            print_format()
        else:
            logging.info("Running %s Finished" % sections[i])
    return 0


def parsing_run():
    # get the test cases defined files
    config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
    fp = open(config_files, 'r')
    tool_list = []
    case_list = yaml.load(fp.read())
    for dimension in case_list:
        for i in range(len(case_list[dimension])):
            for tool in case_list[dimension][i]:
                for case in case_list[dimension][i][tool]:
                    if case_list[dimension][i][tool][case][0] == 'enable':
                        tool_list.append(tool)
    sections = list(set(tool_list))
    dic = {}

    for i in range(0, len(sections)):
        dic[sections[i]] = {}
        # try to resolve the configuration of the configuration file
        try:
            run_file = sections[i] + '_run.cfg'
            parser = sections[i] + '_parser.py'
        except Exception:
            raise AttributeError("The is no option value of parser")

        print_format()
        logging.info("Parsing %s" % sections[i])
        bench = os.path.join(caliper_path.BENCHS_DIR, sections[i], 'defaults')

        try:
            result = parse_all_cases(bench,sections[i], parser, dic)
        except Exception:
            logging.info("Parsing %s Exception" % sections[i])
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
                              + "/final_parsing_logs.yaml"), 'w')
    outfp.write(yaml.dump(dic, default_flow_style=False))
    outfp.close()
    return 0


def print_format():
    logging.info("=" * 55)


def run_caliper_tests(f_option):
    # f_option =1 if -f is used
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
    try:
        logging.debug("beginnig to run the test cases")
        test_result = caliper_run()
    except error.CmdError:
        logging.info("There is wrong in running benchmarks")
        flag = 1
    else:
        if test_result:
            flag = test_result
    return flag


def parser_caliper_tests(flag):
    # f_option =1 if -f is used
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
    try:
        logging.debug("beginnig to parse the test cases")
        test_result = parsing_run()
    except error.CmdError:
        logging.info("There is wrong in parsing test cases")
        flag = 1
    else:
        if test_result:
            flag = test_result
    return flag


if __name__ == "__main__":
    caliper_run()
