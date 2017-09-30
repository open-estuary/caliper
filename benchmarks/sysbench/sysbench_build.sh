build() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/sysbench/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null

}

build
