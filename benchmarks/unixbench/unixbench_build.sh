#!/usr/bin/env bash
build_unixbench() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/unixbench/ansible > /dev/null
    ansible-playbook -i '~/caliper_output/configuration/config/hosts' 'site.yml'
    popd > /dev/null

}

build_unixbench
