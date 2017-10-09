build_nbench()
{
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/nbench/ansible/site.yml"
}

build_nbench
