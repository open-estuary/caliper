build_linpack() {
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/linpack/ansible/site.yml"

}

build_linpack
