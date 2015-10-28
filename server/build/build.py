#!/usr/bin/python
## wuyanjun w00291783
## wu.wu@hisilicon.com
## Copyright

import os
import sys
import subprocess
import ConfigParser
import re
import stat
import shutil
import pdb
import logging
import datetime

try:
    import caliper.common as common
except ImportError:
    import common

import caliper.server.utils as server_utils
from caliper.client.shared import error
from caliper.client.shared import caliper_path
from caliper.client.shared.caliper_path import folder_ope as FOLDER

CALIPER_DIR = caliper_path.CALIPER_DIR
GEN_DIR = caliper_path.GEN_DIR
TEST_CFG_DIR = caliper_path.config_files.tests_cfg_dir
#SPV A unique folder name based on the date and time is created in /tmp so that multiple instance of caliper can run.
TMP_DIR = caliper_path.TMP_DIR+"_"+datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")

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

    f= open(filename, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

def find_benchmark(filename, version, dir_name, build_file):
    """
    check if the benchmarks contained by the benchmarks

    this function should be more
    """
    flag = 0
    benchs_dir = caliper_path.BENCHS_DIR
    current_bench = os.path.join(benchs_dir, filename)
    if os.path.exists(current_bench):
        flag = 1
    if os.path.exists(os.path.join(CALIPER_DIR, filename)):
        flag = 1
    if not flag:
        build_path = os.path.join(TEST_CFG_DIR, dir_name, filename, build_file)
        fp = open(build_path)
        content = fp.read()
        try:
            filename = re.findall('SrcPath.*}\"(.*)\"')[0]
        except Exception:
            filename = ""
        if os.path.exists(os.path.join(benchs_dir, filename)):
            flah = 1
        fp.close()

    bench_dir = ''
    if not version:
        # have not information about the version
        listfile = os.listdir(benchs_dir)
        for line in listfile:
            if re.search(filename, line, re.IGNORECASE):
                flag = 1
                bench_dir = line
    return [bench_dir, flag ]

def generate_build(config, section_name, dir_name, build_file, flag=0):
    """
    generate the final build.sh for each section in common_cases_def
    :param config: the config file for selecting which test case will be run
    :param section_name:the section in config
    param: dir_name: indicate the directory name, like 'common', 'server' and
                        others
    param: build_file: means the final build.sh
    """
    try:
        version = config.get(section_name, 'version')
    except BaseException:
        version = ""
    if version:
        filename = section_name + '_' + version
    else:
        filename = section_name
    """we think that if we store the benchmarks in the directory of benchmarks,
    we need not download the benchmark. if the benchmarks are in the root
    directory of Caliper, we think it is temporarily, after compiling we will
    delete them."""

    try:
        tmp_build = config.get(section_name, 'build')
    except BaseException:
        tmp_build = ""

    ben_dir, exist = find_benchmark(filename, version, dir_name, tmp_build)

    """how to use the ben_dir to build the benchmark"""
    if not exist:
        try:
            download_url = config.get(section_name, 'download_cmd')
        except BaseException:
            logging.info( "We don't have the benchmarks, you should provide a\
                    link to git clone")
            raise
        else:
            url_list = download_url.split(" ")
            # need to expand here
            exit = git(url_list[1], url_list[2])
            if ( exit != 0 ):
                logging.info("Download the benchmark of %s failed" % filename)
                return -2

    """add the build file to the build.sh;  if the build option in it, we add it;
    else we give up the build of it."""
    location = -2
    if tmp_build:
        build_command = os.path.join(TEST_CFG_DIR, dir_name,
                                        section_name, tmp_build)
        file_path = "source " + build_command +"\n"
        insert_content_to_file(build_file, location, file_path)
    else:
    #SPV when is this else part hit?    
        source_fp = open(build_file, "r")
        all_text = source_fp.read()
        source_fp.close()
        func_name = 'build_'+ section_name
        if re.search(func_name, all_text):
            value = func_name + "  \n"
            insert_content_to_file(build_file, location, value)
    return 0

def build_caliper(target_arch, flag=0):
    """
    target_arch means to build the caliper for the special arch
    flag mean build for the target or local machine (namely server)
        0: means for the target
        1: means for the server
    """

    if target_arch:
        arch = target_arch
    else:
        arch = 'x86_64'
    # get the files list of 'cfg'
    cases_file = []
    files_list = server_utils.get_cases_def_files( arch )
    logging.debug("config files are %s" %  files_list)

    
    source_build_file = caliper_path.SOURCE_BUILD_FILE 
    des_build_file = os.path.join(TMP_DIR, caliper_path.BUILD_FILE)
    logging.info("destination file of building is %s" % des_build_file)

    for i in range(0, len(files_list)):
        #get the directory, such as 'common','server' and so on
        dir_name = files_list[i].strip().split("/")[-1].split("_")[0]

        config = ConfigParser.ConfigParser()
        config.read(files_list[i])

        sections = config.sections()
        for i in range(0, len(sections)):
            if os.path.exists(des_build_file):
                os.remove(des_build_file)
            shutil.copyfile(os.path.abspath(source_build_file), des_build_file )
            
            try:
                result = generate_build(config, sections[i],
                                        dir_name, des_build_file)
            except Exception, e:
                logging.info(e)
            else:
                if result:
                    return result
            result = build_each_tool(dir_name, sections[i],
                                        des_build_file, target_arch)
            if os.path.exists(des_build_file):
                os.remove(des_build_file)
            if result:
                build_flag = server_utils.get_fault_tolerance_config("fault_tolerance","build_error_continue")
                if build_flag == 1:
                    continue
                else:
                    return result
    return 0

def build_each_tool(dirname, section_name, des_build_file, arch='x86_86'):
    """
    generate build.sh file for each benchmark tool and run the build.sh
    """
    
    os.chmod( des_build_file, stat.S_IRWXO + stat.S_IRWXU + stat.S_IRWXG )
    logging.info("=========================================================")
    logging.info("Building %s" % section_name)

    log_name = "%s.log" % section_name
    log_file = os.path.join(TMP_DIR, log_name)
    start_time = datetime.datetime.now()
    try:
# Fixme : Using shell=True can be a security hazard. See the warning under https://docs.python.org/2/library/subprocess.html?highlight=subprocess.call#frequently-used-arguments. 
        result = subprocess.call("echo '$$ %s BUILD START: %s' >> %s"
                                    % (section_name, str(start_time)[:19],
                                        FOLDER.caliper_log_file), shell=True)
        result = subprocess.call("%s %s %s %s >> %s 2>&1"
                                    % (des_build_file, arch,
                                        CALIPER_DIR,TMP_DIR, log_file),
                                        shell=True)
    except Exception, e:
        logging.info('There is exception when building the benchmarks')
        raise
    else:
        end_time = datetime.datetime.now()
        subprocess.call("echo '$$ %s BUILD STOP: %s' >> %s"
                         % (section_name, str(end_time)[:19], FOLDER.caliper_log_file),
                            shell=True)
        subprocess.call("echo '$$ %s BUILD DURATION: %s Seconds' >> %s"
                              % (section_name, (end_time-start_time).seconds,
                                  FOLDER.caliper_log_file), shell=True)
        if result:
            logging.info("Building Failed")
            logging.info("====================================================")
            record_log(log_file, arch, 0)
        else:
            logging.info("Building Successful")
            logging.info("====================================================")
            record_log(log_file, arch, 1)
    server_config = server_utils.get_server_cfg_path(
                                    os.path.join(dirname, section_name))
# Not sure the server_config related section to be retained...    
    if (server_config != ''):
        local_arch = server_utils.get_local_machine_arch()
        if (local_arch != arch):
            result = subprocess.call("%s %s %s> %s 2>&1" 
                                    % (des_build_file, local_arch,
                                        CALIPER_DIR, log_file),
                                        shell=True )
            end_time = datetime.datetime.now()
            subprocess.call("echo '$$ %s BUILD STOP: %s' >> %s"
                            % (section_name,str(end_time)[:19], FOLDER.caliper_log_file),
                                shell=True)
            subprocess.call("echo '$$ %s BUILD DURATION %s Seconds' >> %s"
                            % (section_name, (end_time-start_time).seconds,
                                FOLDER.caliper_log_file), shell=True)
            if result:
                record_log(log_file, local_arch, 0)
            else:
                record_log(log_file, local_arch, 1)
            logging.debug("There is exception when building the benchmarks\
                        for localhost")
    return result

def record_log(log_file, arch, succeed_flag):
    build_log_dir= FOLDER.build_dir

    new_name_pre = log_file.split('/')[-1].split('.')[0] + '_' + arch
    pwd = os.getcwd()
    os.chdir(build_log_dir)
    subprocess.call("rm -fr %s*" % new_name_pre , shell=True )
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
        #shutil.move(new_log_name, build_log_dir)
    except Exception, e:
        raise e

def build_for_target(target):

   # Create the temperory build folders 
   if not os.path.exists(os.path.join(TMP_DIR, 'caliper_build')):
       os.makedirs(os.path.join(TMP_DIR, 'caliper_build'), 0755)

   # Improvement Point: Right now all the benchmarks are copied, we can only copy the selected benchmarks to save the time. 
   benchs_dir = os.path.join(TMP_DIR, 'caliper_build', 'benchmarks')
   if os.path.exists(benchs_dir):
      shutil.rmtree(benchs_dir)
   shutil.copytree(caliper_path.BENCHS_DIR, benchs_dir)
   
   
   if os.path.exists(FOLDER.caliper_log_file):
       os.remove(FOLDER.caliper_log_file)
   
   if os.path.exists(FOLDER.summary_file):
       os.remove(FOLDER.summary_file)
   
   if os.path.exists(FOLDER.build_dir):
        shutil.rmtree(FOLDER.build_dir)
   os.mkdir(FOLDER.build_dir, 0755)
   
   if os.path.exists(FOLDER.exec_dir):
        shutil.rmtree(FOLDER.exec_dir)
   os.mkdir(FOLDER.exec_dir, 0755)
   
   if os.path.exists(FOLDER.results_dir):
        shutil.rmtree(FOLDER.results_dir)
   os.mkdir(FOLDER.results_dir, 0755)
   
   if os.path.exists(FOLDER.yaml_dir):
        shutil.rmtree(FOLDER.yaml_dir)
   os.mkdir(FOLDER.yaml_dir, 0755)
   
   if os.path.exists(FOLDER.html_dir):
        shutil.rmtree(FOLDER.html_dir)
   os.mkdir(FOLDER.html_dir, 0755)
   
   if server_utils.get_target_ip(target) in server_utils.get_local_ip():
       return build_for_local()

   try:
      host_arch = server_utils.get_local_machine_arch()
   except Exception, e:
       logging.debug(" Error in get_local_machine_arch()")
       raise e
# This call assign target_arch with target architecture. Call "get_host_arch" looks to be confusing :(   
   target_arch = server_utils.get_host_arch(target)
   target_arch_dir = os.path.join(GEN_DIR, target_arch)
   if os.path.exists(target_arch_dir):
       shutil.rmtree(target_arch_dir)
   os.makedirs(target_arch_dir, 0755)    

# Why should we check and remove local architecture folder??? 
   host_arch_dir = os.path.join(GEN_DIR, host_arch)
   if os.path.exists(host_arch_dir):
       shutil.rmtree(host_arch_dir)

   logging.info(" ")
   logging.info(" Local Host Arch : %s" %host_arch)
   logging.info(" Target Arch : %s" %target_arch)
   logging.info(" Caliper reports and logs are stored : %s" %FOLDER.name)
   logging.info(" Caliper build directory : %s" %TMP_DIR)
   logging.info(" ")

   
   try:
#Build all caliper benchmarks for the target architecture
       result = build_caliper(target_arch, 0)
   except Exception,e:
       raise
   else:
       if result:
          return result
   

#Copy generated binaries to target machine
   result = copy_gen_to_target(target, target_arch)
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
            target.run("mkdir caliper")
        target.run("cd caliper;  mkdir -p binary")
        remote_pwd = target.run("pwd").stdout
        remote_pwd = remote_pwd.split("\n")[0]
        remote_caliper_dir = os.path.join(remote_pwd, "caliper")
        remote_gen_dir = os.path.join(remote_caliper_dir, "binary", target_arch)
        send_file_relative = ['client', 'common.py',  '__init__.py']
        send_files = [ os.path.join(CALIPER_DIR, i) for i in
                send_file_relative]
        send_gen_files= os.path.join( GEN_DIR, target_arch)

        for i in range(0, len(send_files)):
            try:
                target.send_file(send_files[i], remote_caliper_dir)
            except Exception, e:
                logging.info("There is error when coping files to remote %s"
                                % target.ip)
                logging.info( e )
                raise
        target.send_file(send_gen_files, remote_gen_dir)
        logging.info("finished the scp caliper to the remote host")
        return 0

def build_for_local():
    arch = server_utils.get_local_machine_arch()
    logging.info("arch of the local host is %s" % arch)
    arch_dir = os.path.join(GEN_DIR, arch)
    if os.path.exists(arch_dir):
        shutil.rmtree(arch_dir)
    try:
        result = build_caliper(arch, 0)
    except Exception, e:
        raise Exception(e.args[0], e.args[1])
    else:
        return result

if __name__=="__main__":
    build_for_local()
