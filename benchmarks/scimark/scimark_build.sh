build_scimark() {
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/scimark/ansible/site.yml"
}

build_scimark
