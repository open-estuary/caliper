build_OpenBLAS() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/openblas/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_OpenBLAS

