#!/bin/bash

g_FILE=$(basename ${0})
. $(dirname ${0})/${g_FILE%%.*}.common

g_drPro=$(Pure2Dir "${PWD}" "$(dirname ${0})")
g_FILE=$(basename ${0})

#####################
#do
IFS=$'\n'; for d1 in ${g_drPlatform}; do IFS=${g_IFS0};
    sFls=$(find ${d1} -type f -name "*_score.yaml")
    IFS=$'\n'; for f1 in ${sFls}; do IFS=${g_IFS0};
        cp ${f1} ${g_drWInputLogs}/Input_Report/.
    IFS=$'\n'; done; IFS=${g_IFS0};
IFS=$'\n'; done; IFS=${g_IFS0};

IFS=$'\n'; for d1 in ${g_drPlatform}; do IFS=${g_IFS0};
    sFls=$(find ${d1} -type f -name "*_hw_info.yaml")
    IFS=$'\n'; for f1 in ${sFls}; do IFS=${g_IFS0};
        cp ${f1} ${g_drWInputLogs}/Input_Hardware/.
    IFS=$'\n'; done; IFS=${g_IFS0};
IFS=$'\n'; done; IFS=${g_IFS0};

nMax=5
IFS=$'\n'; for d1 in ${g_drPlatform}; do IFS=${g_IFS0};
    sFls=$(find ${d1} -type f -name "*.yaml" |grep "/yaml/" |grep -v "_score\.yaml" |grep -v "_hw_info\.yaml")
    IFS=$'\n'; for f1 in ${sFls}; do IFS=${g_IFS0};
        cp ${f1} ${g_drWInputLogs}/Input_Consolidated/.
        n1=0
        while [ ${n1} -lt ${nMax} ]; do
            let n1+=1
            cp ${f1} ${g_drWInputLogs}/Input_Cov/${n1}/.
        done
    IFS=$'\n'; done; IFS=${g_IFS0};
IFS=$'\n'; done; IFS=${g_IFS0};

sOpenssl=openssl_output.log
IFS=$'\n'; for d1 in ${g_drPlatform}; do IFS=${g_IFS0};
    sFls=$(find ${d1} -type f -name "${sOpenssl}" |grep -v "/test_cases_cfg/")
    sPlatformNames=$(echo "${sFls}" |sed "s#_WS_[0-9_-]\+/output/caliper_exec/${sOpenssl}##;s#^.*/##")
    IFS=$'\n'; for f1 in ${sFls}; do IFS=${g_IFS0};
        cp ${f1} ${g_drWInputLogs}/Input_Openssl/${sPlatformNames}_${sOpenssl}
    IFS=$'\n'; done; IFS=${g_IFS0};
IFS=$'\n'; done; IFS=${g_IFS0};

#####################

