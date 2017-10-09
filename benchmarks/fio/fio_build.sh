build_fio()
{
    CURDIR=$(cd `dirname $0`; pwd)
    cd ~/caliper_output/configuration/config
    ansible-playbook -i hosts ${CURDIR}/benchmarks/fio/ansible/site.yml
}

build_fio

