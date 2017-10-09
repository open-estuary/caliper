#!/bin/bash

build_scimarkJava() {
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/scimarkJava/ansible/site.yml"

}

build_scimarkJava

