build_iozone() {    
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/iozone/ansible/site.yml"
}

build_iozone
