#!/usr/bin/env bash
build_unixbench() {
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/unixbench/ansible/site.yml"

}

build_unixbench
