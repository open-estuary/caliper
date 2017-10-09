#!/usr/bin/env bash
build_unixbench() {
    CURDIR=$(cd `dirname $0`; pwd)
    cd ~/caliper_output/configuration/config
    ansible-playbook -i hosts ${CURDIR}/benchmarks/unixbench/ansible/site.yml

}

build_unixbench
