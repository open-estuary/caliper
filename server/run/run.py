#!/usr/bin/env python

import os
import sys
import time
import shutil
import re
import logging
import datetime
import subprocess

import yaml
import threading

try:
    import caliper.common as common
except ImportError:
    import common
from caliper.server import crash_handle
from caliper.server.shared import error
from caliper.server import utils as server_utils
from caliper.server.shared import caliper_path
from caliper.server.run import write_results
from caliper.server.shared.caliper_path import folder_ope as Folder

class run_case_thread(threading.Thread):
    def __init__(self, bench_name, commands, host):
        threading.Thread.__init__(self)
        self.bench_name = bench_name
        self.commands = commands
        self.host = host

    def run(self):
        returncode = -1
        output = ''
        pwd = os.getcwd()
        try:
            # the commands is multiple lines, and was included by Quotation
            actual_commands = get_actual_commands(self.commands)
            try:
                logging.debug("the actual commands running in local is: %s"
                              % actual_commands)
                test_case_dir = os.path.join(caliper_path.BENCHS_DIR, self.bench_name, 'tests')
                os.chdir(test_case_dir)
                result = subprocess.call(
                    'ansible-playbook %s.yml --extra-vars "hosts=%s" -u root>> %s 2>&1' %
                    (actual_commands, self.host, Folder.caliper_run_log_file), stdout=subprocess.PIPE, shell=True)
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



def caliper_run():
    # get the test cases defined files
    sections, run_case_list = common.read_config()
    for i in range(0, len(sections)):
        # try to resolve the configuration of the configuration file
        try:
            run_file = sections[i]+ '_run.cfg'
            parser = sections[i]+ '_parser.py'
        except Exception:
            raise AttributeError("The is no option value of parser")

        common.print_format()

        logging.info("Running %s" % sections[i])
        bench = os.path.join(caliper_path.BENCHS_DIR, sections[i], 'defaults')
        try:
            # On some platforms, swapoff and swapon command is not able to execute.
            # So this function has been commented
            result = run_all_cases(bench, sections[i], run_case_list)
        except Exception, e:
            logging.info(e)
            logging.info("Running %s Exception" % sections[i])
            crash_handle.main()
            common.print_format()
        else:
            logging.info("Running %s Finished" % sections[i])
    return 0

def run_all_cases(kind_bench, bench_name, run_case_list):
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
    for section in sections_run:
        if section in run_case_list:
            num = 1
            config_files = os.path.join(caliper_path.config_files.config_dir, 'cases_config.json')
            fp = open(config_files, 'r')
            case_list = yaml.load(fp.read())
            for dimension in case_list:
                for i in range(len(case_list[dimension])):
                    for tool in case_list[dimension][i]:
                        for case in case_list[dimension][i][tool]:
                            if case == section:
                                num = case_list[dimension][i][tool][case][-1]
            flag = 0
            try:
                command = values[bench_name][section]['command']
            except Exception:
                logging.debug("no value for the %s" % section)
                continue

            if os.path.exists(tmp_log_file):
                os.remove(tmp_log_file)
            # run the command of the benchmarks

            try:
                for j in range(int(num)):
                    subprocess.call("echo 'the %s time'>>%s" % (j, Folder.caliper_run_log_file), shell=True)
                    flag = run_client_command(section, tmp_log_file, command, bench_name)
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
        else:
            continue

        endtime = datetime.datetime.now()
        subprocess.call("echo '$$ %s EXECUTION STOP: %s' >> %s"
                                 % (section, str(endtime)[:19],
                                    Folder.caliper_log_file), shell=True)
        subprocess.call("echo '$$ %s EXECUTION DURATION %s Seconds'>>%s"
                                 % (section,
                                    (endtime - starttime).seconds,
                                    Folder.caliper_log_file), shell=True)

        subprocess.call("echo '$$ %s RUN STOP: %s' >> %s"
                                 % (section, str(endtime)[:19],
                                    Folder.caliper_run_log_file), shell=True)
        subprocess.call("echo '$$ %s RUN DURATION %s Seconds'>>%s"
                                 % (section,
                                    (endtime - starttime).seconds,
                                    Folder.caliper_run_log_file), shell=True)
        subprocess.call("echo '======================================================'>>%s"% (Folder.caliper_run_log_file), shell=True)

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
