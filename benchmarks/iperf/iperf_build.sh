build_iperf() {

    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/iperf/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null

}

build_iperf
