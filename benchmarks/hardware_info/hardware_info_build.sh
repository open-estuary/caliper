build_hardware() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/hardware_info/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}
build_hardware
