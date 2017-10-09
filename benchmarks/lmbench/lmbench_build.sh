build_lmbench() {
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/lmbench/ansible/site.yml"
}

build_lmbench
