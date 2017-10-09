build_dhrystone()
{
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/dhrystone/ansible/site.yml"
}

build_dhrystone

