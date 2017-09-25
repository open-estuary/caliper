build_qperf() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/qperf/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_qperf