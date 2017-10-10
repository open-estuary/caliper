build_fio()
{
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/fio/ansible > /dev/null
    ansible-playbook -i ~/caliper_output/configuration/config/hosts site.yml -u root
    popd > /dev/null
}

build_fio

