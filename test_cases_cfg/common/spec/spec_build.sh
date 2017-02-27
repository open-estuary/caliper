
SpecBuild()
{
    #drBench=$(sed "s#/\+\$##" <<< "${BENCH_PATH}")
    drBench=${HOME}/.caliper/benchmarks
    drBenSpec=$(ls -d ${drBench}/*.spec 2>/dev/null)
    drBenSpecArch=${drBenSpec}/${ARCH}
    nRow1=$(wc -l <<< "${drBenSpecArch}")
    if [ -z "${drBenSpecArch}" -o ${nRow1} -ne 1 ]; then
        printf "%s[%3d]%s[%3d]%5s: spec benchmark directory[${drBenSpecArch}] not correct\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Error"
        exit 1
    fi

    drObjSpec="${INSTALL_DIR}/spec"
    mkdir -p ${drObjSpec}
    flList1=$(ls -d ${drBenSpecArch}/* 2>/dev/null)
    flList2=$(ls -d ${drObjSpec}/* 2>/dev/null)
    flSpec1=$(grep -F "${flList1}" <<< "${flList2}")
    if [ $? -eq 0 ]; then
        printf "%s[%3d]%s[%3d]%5s: spec was built already\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Info"
        return 0
    fi

    cp ${drBenSpec}/spec.sh ${drObjSpec}
    cp -r ${drBenSpecArch}/* ${drObjSpec}
}

SpecBuild

#printf "%s[%3d]%s[%3d]%5s: drBench[${drBench}] ${BASH_SOURCE[1]}\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Info"

