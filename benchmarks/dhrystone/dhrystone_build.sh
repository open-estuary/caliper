build_dhrystone()
{
    CURDIR=$(cd `dirname $0`; pwd)
    cd ~/caliper_output/configuration/config
    ansible-playbook -i hosts ${CURDIR}/benchmarks/dhrystone/ansible/site.yml
}

build_dhrystone

