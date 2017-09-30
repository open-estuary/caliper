build_scimark() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/scimark/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_scimark
