build_fio()
{
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/fio/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_fio

