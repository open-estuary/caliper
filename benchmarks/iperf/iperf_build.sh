build_iperf() {

    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/iperf/ansible/site.yml"

}

build_iperf
