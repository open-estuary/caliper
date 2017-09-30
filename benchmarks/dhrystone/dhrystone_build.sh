build_dhrystone()
{
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/dhrystone/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_dhrystone

