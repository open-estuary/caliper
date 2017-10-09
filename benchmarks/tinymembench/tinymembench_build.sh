build() {
    CURDIR=$(cd `dirname $0`; pwd)
    ansible-playbook -i "~/caliper_output/configuration/config/hosts" "${CURDIR}/benchmarks/tinymembench/ansible/site.yml"
}

build

