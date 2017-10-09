build_OpenBLAS() {
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/openblas/ansible/site.yml"
}

build_OpenBLAS

