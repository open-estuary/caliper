#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import yaml
import datetime

try:
    import caliper.common
except ImportError:
    import common

import caliper.server.utils as server_utils
from caliper.client.shared import caliper_path
from caliper.server.hosts import host_factory


def write_yaml_file(dic, filename):
    if filename:
        with open(filename, 'w') as outfile:
            outfile.write(yaml.dump(dic, default_flow_style=False))
            outfile.write('\n')
        outfile.close()


def write_file(filename, content):
    fp = open(filename, 'a')
    fp.write(content)
    fp.write("\n")
    fp.close()


def get_selected_tools(summary_file, target):
    selected_tools = []
    config_files = server_utils.get_cases_def_files(target)

    for i in range(0, len(config_files)):
        config_file = os.path.join(config_files[i])
        config, sections = server_utils.read_config_file(config_file)
        if len(sections):
            selected_tools.extend(sections)
    return selected_tools


def get_builded_tools():
    despath = caliper_path.folder_ope.build_dir
    suc_tools = []
    fail_tools = []
    for root, dirs, files in os.walk(despath):
        for i in range(0, len(files)):
            test_tool_name = '_'.join(files[i].split('_')[0:-2])
            if re.search('.suc', files[i]):
                if test_tool_name not in fail_tools:
                    if test_tool_name not in suc_tools:
                        suc_tools.append(test_tool_name)
            else:
                if test_tool_name in suc_tools:
                    suc_tools.remove(test_tool_name)
                if test_tool_name not in fail_tools:
                    fail_tools.append(test_tool_name)
    return [suc_tools, fail_tools]


def get_exec_tools(selected_tools):
    despath = caliper_path.folder_ope.exec_dir
    pass_tools = []
    partial_tools = []
    failed_tools = []

    fail_flag = "\[status\]\:\s+FAIL"
    suc_flag = "\[status\]\:\s+PASS"
    num = 0

    [suc_build_tools, fail_build_tools] = get_builded_tools()
    if os.path.exists(despath):
        for file_name in os.listdir(despath):
            num += 1
            tool_name = '_'.join(file_name.split('_')[0:-1])
	    flag = 0
	    for tool in selected_tools:
		if tool_name == tool:
		    flag = 1
		    break
	    if flag == 0:
		continue
            file_path = os.path.join(despath, file_name)
            fp = open(file_path, 'r')
            contents = fp.read()

            if re.search(fail_flag, contents):
                if re.search(suc_flag, contents):
                    partial_tools.append(tool_name)
                else:
                    failed_tools.append(tool_name)
            else:
                if re.search(suc_flag, contents):
                    pass_tools.append(tool_name)
            for tool in fail_build_tools:
                try:
                    failed_tools.remove(tool)
                except Exception:
                    continue
    else:
        return (0, 0, 0)
    return (pass_tools, partial_tools, failed_tools)


def write_summary_tools(summary_file, target):
    selected_tools = get_selected_tools(summary_file, target)
    if len(selected_tools):
        selected_num = "\nNum of tools selected: %s" % len(selected_tools)
        write_file(summary_file, selected_num)

    [suc_tools, fail_tools] = get_builded_tools()
    if len(suc_tools):
        build_suc_num = "Num of tools build successfully: %s" % len(suc_tools)
        write_file(summary_file, build_suc_num)
    if len(fail_tools):
        build_failed_num = "Num of tools build failed: %s" % len(fail_tools)
        write_file(summary_file, build_failed_num)

    (suc_tools, partial_tools, failed_tools) = get_exec_tools(selected_tools)
    if len(suc_tools):
        exec_suc_num = "Num of tools run successfully: %s" % len(suc_tools)
        write_file(summary_file, exec_suc_num)
    if len(partial_tools):
        exec_partial_num = "Num of tools run partial successfully: %s" % \
                len(partial_tools)
        write_file(summary_file, exec_partial_num)
    if len(failed_tools):
        exec_failed_num = "Num of tools run failed: %s" % len(failed_tools)
        write_file(summary_file, exec_failed_num)
    write_file(summary_file, '\n')


def write_info_for_tools(filename, target):
    build_suc_info = "Tool %s : Build PASS"
    build_fail_info = "Tool %s : Build Fail"
    exec_suc_info = "Tool %s : Execution PASS\n"
    exec_partial_info = "Tool %s : Execution Partial PASS\n"
    exec_fail_info = "Tool %s : Execution Fail\n"

    selected_tools = get_selected_tools(filename, target)
    if not len(selected_tools):
        return
    [build_suc_tools, build_fail_tools] = get_builded_tools()
    (exec_suc_tools, exec_par_tools, exec_fail_tools) = get_exec_tools(selected_tools)

    for tool in selected_tools:
        if tool in build_suc_tools:
            build_info = build_suc_info % tool
        else:
            build_info = build_fail_info % tool

        if tool in exec_suc_tools:
            exec_info = exec_suc_info % tool
        elif tool in exec_par_tools:
            exec_info = exec_partial_info % tool
        else:
            if tool in build_fail_tools:
                exec_info = ""
            else:
                exec_info = exec_fail_info % tool
        write_file(filename, build_info)
        write_file(filename, exec_info)


def output_summary_info(target, interval):
    summary_file = caliper_path.folder_ope.summary_file
    if os.path.exists(summary_file):
        os.remove(summary_file)

    hardware_info = server_utils.get_host_hardware_info(target)
    write_yaml_file(hardware_info, summary_file)

    used_time = "Total used time: %.4s minutes" % (interval/60.0)
    write_file(summary_file, used_time)

    write_summary_tools(summary_file, target)
    write_info_for_tools(summary_file, target)

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    target = host_factory.create_host('localhost', 'wuyanjun', '', 22)
    end_time = datetime.datetime.now()
    output_summary_info(target, (end_time-start_time).seconds)
