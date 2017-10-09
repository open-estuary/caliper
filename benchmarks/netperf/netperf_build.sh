build_netperf() {
    CURDIR=$(cd `dirname $0`; pwd)
    cd ~/caliper_output/configuration/config
    ansible-playbook -i hosts ${CURDIR}/benchmarks/netperf/ansible/site.yml
}

build_netperf
