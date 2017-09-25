#!/bin/bash

build_scimarkJava() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/scimarkJava/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null

}

build_scimarkJava

