#!/bin/bash

g_pfn="${BASH_SOURCE[0]}"
#current work directory may be will change, so save it first
g_drCur="${PWD}"
g_fln=$(basename "${g_pfn}")
g_drPro=$(dirname "${g_pfn}")

. ${g_drPro}/${g_fln%%.*}.common

g_drPro=$(Pure2Dir "${g_drCur}" "${g_drPro}")
g_pfn="${g_drPro}/${g_fln}"

#####################
#do
sTCIDPre=${1}
sTag1=${2}
sTCIDs=${3}
sCaliperCmd=${4}
sBenchTools=${5}
flLogCaliper=${6}

##########
PureMarkSign sTCIDPre
sTCIDPre=${sTCIDPre}_TC_

sOtherArgs1=$(sed "s/^[ \t]*\(${g_reName}=\)/local \1/" <<< "${sOtherArgs}")
eval "${sOtherArgs1}"
CheckVarDefined varSucc "${sOtherArgs}"
CheckVarDefined varFail "${sOtherArgs}"
CheckVarDefined sArchTarget "${sOtherArgs}"
CheckVarDefined sIPTarget "${sOtherArgs}"

##########
nErrs=0
nIDNo=04
drBinary=~/caliper_output/binary

##########
eval "${sCaliperCmd}" 2>&1 |tee ${flLogCaliper}

#TS_01_TC_03
CheckCondition "" "-d" "${drBinary}" ${sTCIDPre}03 "${sTag1}" sTCIDs all "${varSucc}" "${varFail}"
let nErrs+=$?

#TS_01_TC_04
CheckCaliperOutputDir sPathLogMain "${sCaliperCmd}" "${flLogCaliper}"
CheckCondition "" "-d" "${sPathLogMain}" ${sTCIDPre}${nIDNo} "${sTag1}" sTCIDs false "${varSucc}" "${varFail}"
if [ $? -ne 0 ]; then
    printf "%s[%3d]%5s: [${sPathLogMain}] folder not exist\n" "${FUNCNAME[0]}" ${LINENO} "Error" |tee -a ${g_flBaseLog}.log
    exit 1
fi

#bench tools in log
GetToolNamesFromLog sToolsLog "${flLogCaliper}"
sToolsLog=$(tr '\n' ',' <<< "${sToolsLog}")

#bench tools in configure files
flSetCaliperCfgProCfg="${g_drProSetCaliperCfg}/caliper.cfg"
sTxtCfg=$(cat ${flSetCaliperCfgProCfg})
sTxtModify=
SetSetCaliperCfgCfg g_drBase "${sPathLogMain}" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
if [ -n "${sTxtModify}" ]; then
    echo "${sTxtCfg}" >${flSetCaliperCfgProCfg}
    printf "%s[%3d]%5s: [${flSetCaliperCfgProCfg}] modify:${sTxtModify}\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flBaseLog}.log
fi
sToolsCfg=$(${g_drProSetCaliperCfg}/caliper.GetBenchTools.sh BenchToolsMark)
sToolsCfg=$(grep "[: \t]\+BenchToolsMark[ \t]*:" <<< "${sToolsCfg}" |sed "s/^.*[: \t]\+BenchToolsMark[ \t]*:[ \t]*//")
sToolsCfg=$(grep -v "^[ \t]*#" <<< "${sToolsCfg}")
#printf "%s[%3d]%5s: \n" "${FUNCNAME[0]}" ${LINENO} "Error" |tee -a ${g_flLogStatus}

CheckCondition "${sBenchTools}" "==" "${sToolsCfg}" ${sTCIDPre}${nIDNo} "${sTag1}" sTCIDs false "${varSucc}" "${varFail}"
if [ $? -eq 0 ]; then
    CheckCondition "${sToolsLog}" "==" "${sToolsCfg}" ${sTCIDPre}${nIDNo} "${sTag1}" sTCIDs all "${varSucc}" "${varFail}"
    let nErrs+=$?
else
    let nErrs+=1
fi

##########
exit ${nErrs}

#####################

