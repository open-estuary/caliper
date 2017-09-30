build_nbench()
{
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/nbench/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_nbench
