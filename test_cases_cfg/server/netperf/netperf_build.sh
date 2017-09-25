build_netperf() {

    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/netperf/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null

}

build_netperf
