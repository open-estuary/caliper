build_linpack() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/linpack/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null

}

build_linpack
