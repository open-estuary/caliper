build_OpenBLAS() {
    CURDIR=$(cd `dirname $0`; pwd)
    cd ~/caliper_output/configuration/config
    ansible-playbook -i hosts ${CURDIR}/benchmarks/openblas/ansible/site.yml
}

build_OpenBLAS

