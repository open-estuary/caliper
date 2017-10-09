build_openssl() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/coremark/ansible > /dev/null
    ansible-playbook -i '~/caliper_output/configuration/config/hosts' 'site.yml'
    popd > /dev/null
}

build_openssl

