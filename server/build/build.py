#!/usr/bin/python

import os
import subprocess
import ConfigParser
import re
import stat
import shutil
import logging
import datetime
import yaml
import sys
import signal
import time
import glob
from pwd import getpwnam
import datetime
import json

try:
    import caliper.common as common
except ImportError:
    import common

import caliper.server.utils as server_utils
import caliper.client.shared.utils as client_utils
from caliper.client.shared import error
from caliper.client.shared import caliper_path
from caliper.client.shared.caliper_path import folder_ope as FOLDER

CALIPER_DIR = caliper_path.CALIPER_DIR
GEN_DIR = caliper_path.GEN_DIR
WS_GEN_DIR = os.path.join(FOLDER.workspace,'binary')
TEST_CASE_DIR = caliper_path.config_files.config_dir
BUILD_MAPPING_DIR = os.path.join(GEN_DIR,'build_mapping')
BUILD_MAPPING_FILE = BUILD_MAPPING_DIR
# SPV A unique folder name based on the date and time is created in /tmp so
# that multiple instance of caliper can run.
TMP_DIR = caliper_path.TMP_DIR
currentProcess = [0,os.getpid()]

signal_ingored = [signal.SIGINT,signal.SIGTERM,signal.SIGALRM,signal.SIGHUP]
original_sigint = [None]*len(signal_ingored)

def copy_dic(src,dest,skip):
    try:
        for section in src.keys():
            if section not in dest.keys():
                dest[section] = src[section]
    except :
        pass

def reset_binary_mapping():
    global BUILD_MAPPING_FILE
    global currentProcess

    with client_utils.SimpleFlock(BUILD_MAPPING_FILE, 60):
        fp = open(BUILD_MAPPING_FILE)
        dic = yaml.load(fp)
        fp.close()
        try:
            for section in dic.keys():
                if dic[section]['ProcessID'] in currentProcess:
                    if not dic[section]['binaries']:
                        del dic[section]
                    else:
                        dic[section]['ProcessID'] = 0
        except Exception as e:
            logging.debug(e)
            pass
        fp = open(BUILD_MAPPING_FILE,'w')
        fp.write(yaml.dump(dic, default_flow_style=False))
        fp.close()

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    global original_sigint
    global signal_ingored
    global BUILD_MAPPING_FILE
    for i in range(len(signal_ingored)):
        signal.signal(signal_ingored[i], original_sigint[i])
    try:
        reset_binary_mapping()
    except Exception as e:
        logging.error(e)
    sys.exit(1)

    # restore the exit gracefully handler here
    # signal.signal(signal.SIGINT, exit_gracefully)


def set_signals():
    global original_sigint
    global signal_ingored
    for i in range(len(signal_ingored)):
        original_sigint[i] = signal.getsignal(signal_ingored[i])
        signal.signal(signal_ingored[i], exit_gracefully)

def reset_signals():
    global original_sigint
    global signal_ingored
    for i in range(len(signal_ingored)):
        signal.signal(signal_ingored[i], signal.SIG_DFL)


def git(*args):
    return subprocess.check_call(['git'] + list(args))


def svn(*args):
    return subprocess.check_call(['svn'] + list(args))


def insert_content_to_file(filename, index, value):
    """
    insert the content to the index lines
    :param filename: the file will be modified
    :param index: the location eill added the value
    :param value: the content will be added
    """
    f = open(filename, "r")
    contents = f.readlines()
    f.close()

    contents.insert(index, value)

    f = open(filename, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()


def generate_build(section_name, build_file, flag=0):
    """
    generate the final build.sh for each section in common_cases_def
    :param config: the config file for selecting which test case will be run
    :param section_name:the section in config
    param: dir_name: indicate the directory name, like 'common', 'server' and
                        others
    param: build_file: means the final build.sh
    """
    """
    we think that if we store the benchmarks in the directory of benchmarks,
    we need not download the benchmark. if the benchmarks are in the root
    directory of Caliper, we think it is temporarily, after compiling we will
    delete them.
    """

    try:
        tmp_build = section_name + '_build.sh'
    except BaseException:
        tmp_build = ""

    """add the build file to the build.sh;  if the build option in it,
    we add it; else we give up the build of it."""
    location = -2
    if tmp_build:
        build_command = os.path.join(TEST_CASE_DIR, section_name, tmp_build)
        file_path = "source " + build_command + "\n"
        insert_content_to_file(build_file, location, file_path)
    else:
        # SPV when is this else part hit?
        source_fp = open(build_file, "r")
        all_text = source_fp.read()
        source_fp.close()
        func_name = 'build_' + section_name
        if re.search(func_name, all_text):
            value = func_name + "  \n"
            insert_content_to_file(build_file, location, value)
    return 0


def getAllFilesRecursive(root):
    files = [os.path.join(root, f) for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    dirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    for d in dirs:
        files_in_d = getAllFilesRecursive(os.path.join(root, d))
        if files_in_d:
            for f in files_in_d:
                files.append(os.path.join(root, f))
    return files

def build_caliper(target_arch, flag=0,clear=0):
    """
    target_arch means to build the caliper for the special arch
    flag mean build for the target or local machine (namely server)
        0: means for the target
        1: means for the server
    """
    copy = 0
    global GEN_DIR, WS_GEN_DIR,BUILD_MAPPING_FILE,BUILD_MAPPING_DIR
    GEN_DIR = caliper_path.GEN_DIR
    WS_GEN_DIR = os.path.join(FOLDER.workspace, 'binary')

    prev_build_files = []
    current_build_files = []
    WS_prev_build_files = []
    WS_current_build_files = []

    if target_arch:
        arch = target_arch
    else:
        arch = 'x86_64'
    # get the files list of 'cfg'
    case_file = os.path.join(TEST_CASE_DIR, 'cases_config.json')
    fp = open(case_file, 'r')
    build_list = []
    case_list = json.load(fp)
    BUILD_MAPPING_DIR = os.path.join(BUILD_MAPPING_DIR,arch)
    if not os.path.exists(BUILD_MAPPING_DIR):
        try:
            os.makedirs(BUILD_MAPPING_DIR)
        except:
            pass
    source_build_file = caliper_path.SOURCE_BUILD_FILE
    des_build_file = os.path.join(TMP_DIR, caliper_path.BUILD_FILE)
    logging.info("destination file of building is %s" % des_build_file)
    set_signals()

    # {"dimension":[{"tool":[{"case1":["enable","1"]}, {"case2":["enable","1"]},]}]}
    for dimension in case_list:
        for i in range(len(case_list[dimension])):
            for tool in case_list[dimension][i]:
                for case in case_list[dimension][i][tool]:
                    if case_list[dimension][i][tool][case][0] == 'enable':
                        build_list.append(tool)
    build_list = list(set(build_list))

    # check and delete those binaries if it is already built if -c is used
    if clear:
        logging.info("=" * 55)
        logging.info("WARNING: Please wait, dont run any other instance of caliper")
        for section in build_list:
            BUILD_MAPPING_FILE = os.path.join(BUILD_MAPPING_DIR, section + '.yaml')
            with client_utils.SimpleFlock(BUILD_MAPPING_FILE, 60):
                fp = open(BUILD_MAPPING_FILE)
                dic = yaml.load(fp)
                fp.close()
                if type(dic) != dict:
                    dic = {}
                if section in dic.keys():
                    for file in dic[section]['binaries']:
                        try:
                            shutil.rmtree(file)
                        except:
                            pass
                    dic[section]['binaries'] = []
                    dic[section]['ProcessID'] = 0
                fp = open(BUILD_MAPPING_FILE, 'w')
                fp.write(yaml.dump(dic, default_flow_style=False))
                fp.close()
        logging.info("It is safe to run caliper now")
        logging.info("=" * 55)

    for section in build_list:
        BUILD = 0
        BUILD_MAPPING_FILE = os.path.join(BUILD_MAPPING_DIR, section + '.yaml')
        reset_binary_mapping()

        try:
            #Lock the file and modify it if this is the first process which is building the tool
            with client_utils.SimpleFlock(BUILD_MAPPING_FILE, 60):
                fp = open(BUILD_MAPPING_FILE)
                dic = yaml.load(fp)
                if type(dic) != dict:
                    dic = {}
                fp.close()
                if section not in dic.keys():
                    dic[section] = {}
                    dic[section]['binaries'] = []
                    dic[section]['ProcessID'] = os.getpid()
                    BUILD = 1
                fp = open(BUILD_MAPPING_FILE, 'w')
                fp.write(yaml.dump(dic, default_flow_style=False))
                fp.close()

            #checking if binary field is empty, empty means that the previous build is a failure
            if not dic[section]['binaries']:
                BUILD = 1

            # Checking if the tool if already built or is in the process of being built by another process
            if dic[section]['ProcessID'] not in currentProcess:
                # We shall continue to build the next tools and we'll copy these binaries later
                logging.info("=" * 55)
                # logging.info("%s is being built by someother process, we'll build the remaining tools" % sections[i])
                # continue
        except Exception as e:
            logging.debug(e)
            sys.exit(1)

        BUILD = 1
        if BUILD == 1:
            if os.path.exists(des_build_file):
                os.remove(des_build_file)
            shutil.copyfile(os.path.abspath(source_build_file), des_build_file)

            logging.info("=" * 55)
            logging.info("Building %s" % section)
            build_dir = os.path.join(caliper_path.BENCHS_DIR, section, 'tests')
            log_name = "%s.log" % section
            log_file = os.path.join('/tmp', log_name)
            os.chdir(build_dir)
            try:
                # result = os.popen('ansible-playbook -i %s/hosts site.yml -u root>> %s 2>&1' % (TEST_CASE_DIR, log_file))
                result = subprocess.call('ansible-playbook -i %s/hosts site.yml -u root>> %s 2>&1' %(TEST_CASE_DIR, log_file), stdout=subprocess.PIPE, shell=True)
            except Exception as e:
                result = e
            for k in range(len(case_list['network'])):
                if section in case_list['network'][k]:
                    try:
                        subprocess.Popen(
                            'ansible-playbook -i %s/hosts runserver.yml -u root' % (TEST_CASE_DIR), stdout=subprocess.PIPE, shell=True)
                    except Exception as e:
                        pass
            if result:
                logging.info("Building Failed")
                logging.info("=" * 55)
                record_log(log_file, arch, 0)
            else:
                logging.info("Building Successful")
                logging.info("=" * 55)
                record_log(log_file, arch, 1)

    reset_signals()
    return 0

def record_log(log_file, arch, succeed_flag):
    build_log_dir = FOLDER.build_dir
    main_build_dir = os.path.join(caliper_path.BUILD_LOGS, arch)
    if not os.path.exists(main_build_dir):
        os.makedirs(main_build_dir)
        os.chown(main_build_dir, getpwnam(os.environ['HOME'].split('/')[-1]).pw_uid, -1)
    new_name_pre = log_file.split('/')[-1].split('.')[0] + '_' + arch
    pwd = os.getcwd()
    os.chdir(build_log_dir)
    subprocess.call("rm -fr %s*" % new_name_pre, shell=True)
    os.chdir(pwd)

    if (succeed_flag == 1):
        new_log_name = new_name_pre + '.suc'
    else:
        new_log_name = new_name_pre + '.fail'
        
    try:
        shutil.move(log_file, build_log_dir)
        current_file = os.path.join(FOLDER.build_dir, log_file.split("/")[-1])
        new_log_name = os.path.join(FOLDER.build_dir, new_log_name)
        os.rename(current_file, new_log_name)
        pwd = os.getcwd()
        os.chdir(main_build_dir)
        subprocess.call("rm -fr %s*" % new_name_pre, shell=True)
        os.chdir(pwd)
        shutil.copy(new_log_name,main_build_dir)
    except Exception, e:
        raise e


def create_folder(folder, mode=0755):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    try:
        os.mkdir(folder, mode)
    except OSError:
        os.makedirs(folder, mode)

def build_for_target(target,f_option,clear):
    #f_option is set if -f is used
    # Create the temperory build folders
    GEN_DIR = caliper_path.GEN_DIR
    WS_GEN_DIR = os.path.join(FOLDER.workspace, 'binary')

    benchs_dir = os.path.join(TMP_DIR, 'benchmarks')
    if not os.path.exists(benchs_dir):
        try:
            os.makedirs(benchs_dir, 0755)
        except Exception:
            os.mkdir(benchs_dir, 0755)

    # Improvement Point: Right now all the benchmarks are copied, we can only
    # copy the selected benchmarks to save the time.
    if os.path.exists(benchs_dir):
        shutil.rmtree(benchs_dir)
    shutil.copytree(caliper_path.BENCHS_DIR, benchs_dir)

    if not os.path.exists(caliper_path.FRONT_END_DIR):
        shutil.copytree(caliper_path.FRONT_TMP_DIR,
                caliper_path.FRONT_END_DIR)
    if f_option == 0:
        if os.path.exists(FOLDER.caliper_log_file):
            os.remove(FOLDER.caliper_log_file)

        if os.path.exists(FOLDER.summary_file):
            os.remove(FOLDER.summary_file)
    if not os.path.exists(FOLDER.build_dir):
        create_folder(FOLDER.build_dir)
    if not os.path.exists(FOLDER.exec_dir):
        create_folder(FOLDER.exec_dir)
    if not os.path.exists(FOLDER.results_dir):
        create_folder(FOLDER.results_dir)
    if not os.path.exists(FOLDER.yaml_dir):
        create_folder(FOLDER.yaml_dir)
    if not os.path.exists(FOLDER.html_dir):
        create_folder(FOLDER.html_dir)
    if not os.path.exists(caliper_path.HTML_DATA_DIR_INPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_INPUT)
    if not os.path.exists(caliper_path.HTML_DATA_DIR_OUTPUT):
        os.makedirs(caliper_path.HTML_DATA_DIR_OUTPUT)

    # This call assign target_arch with target architecture. Call
    # "get_host_arch" looks to be confusing :(
    target_arch = server_utils.get_host_arch(target)
    target_arch_dir = os.path.join(GEN_DIR, target_arch)
    if not os.path.exists(target_arch_dir):
        create_folder(target_arch_dir, 0755)
    WS_target_arch_dir = os.path.join(WS_GEN_DIR, target_arch)
    create_folder(WS_target_arch_dir, 0755)

    # Why should we check and remove local architecture folder???
    # host_arch_dir = os.path.join(GEN_DIR, host_arch)
    # if os.path.exists(host_arch_dir):
    #    shutil.rmtree(host_arch_dir)

    if server_utils.get_target_ip(target) in server_utils.get_local_ip():
        return build_for_local()

    try:
        host_arch = server_utils.get_local_machine_arch()
    except Exception, e:
        logging.debug(" Error in get_local_machine_arch()")
        raise e

    logging.info(" ")
    logging.info(" Local Host Arch : %s" % host_arch)
    logging.info(" Target Arch : %s" % target_arch)
    logging.info(" Caliper reports and logs are stored : %s" % FOLDER.workspace)
    logging.info(" Caliper build directory : %s" % TMP_DIR)
    logging.info(" ")

    try:
        # Build all caliper benchmarks for the target architecture
        result = build_caliper(target_arch, flag=0,clear=clear)
    except Exception:
        raise
    else:
        if result:
            return result

    # Copy generated binaries to target machine
    result = copy_gen_to_target(target, target_arch)
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    return result


def copy_gen_to_target(target, target_arch):
    try:
        result = target.run("test -d caliper", ignore_status=True)
    except error.ServRunError, e:
        raise
    else:
        if not result.exit_status:
            target.run("cd caliper; rm -fr *; cd")
        else:
            target.run("rm -fr caliper; mkdir caliper")
        target.run("cd caliper;  mkdir -p binary")
        remote_pwd = target.run("pwd").stdout
        remote_pwd = remote_pwd.split("\n")[0]
        remote_caliper_dir = os.path.join(remote_pwd, "caliper")
        remote_gen_dir = os.path.join(remote_caliper_dir, "binary",
                                        target_arch)
        send_file_relative = ['client', 'common.py',  '__init__.py']
        send_files = [os.path.join(CALIPER_DIR, i) for i in
                send_file_relative]
        send_gen_files = os.path.join(GEN_DIR, target_arch)

        for i in range(0, len(send_files)):
            try:
                target.send_file(send_files[i], remote_caliper_dir)
            except Exception, e:
                logging.info("There is error when coping files to remote %s"
                                % target.ip)
                logging.info(e)
                raise
        target.send_file(send_gen_files, remote_gen_dir)
        logging.info("finished the scp caliper to the remote host")
        return 0

def copy_gen_to_server(target, path):
    try:
        result = target.run("test -d caliper_server", ignore_status=True)
    except error.ServRunError, e:
        raise
    else:
        if result.exit_status:
            target.run("mkdir -p caliper_server")

        remote_pwd = target.run("pwd").stdout
        remote_pwd = remote_pwd.split("\n")[0]
        remote_caliper_dir = os.path.join(remote_pwd, "caliper_server")
        try:
            target.send_file(path, remote_caliper_dir)
        except Exception, e:
            logging.info("There is error when coping files to remote %s"
                                % target.ip)
            logging.info(e)
            raise
        logging.info("finished the scp server script to the remote host")
        return 0

def build_for_local():
    arch = server_utils.get_local_machine_arch()
    logging.info("arch of the local host is %s" % arch)
    arch_dir = os.path.join(GEN_DIR, arch)
    # if os.path.exists(arch_dir):
    #     shutil.rmtree(arch_dir)
    try:
        result = build_caliper(arch, flag=0, clear=0)
    except Exception, e:
        raise Exception(e.args[0], e.args[1])
    else:
        return result

if __name__ == "__main__":
    build_for_local()
