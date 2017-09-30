build() {

    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/stressng/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null

}

build