build_fio()
{
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/fio/ansible/site.yml"
}

build_fio

