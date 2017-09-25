build_iozone() {    
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/iozone/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_iozone
