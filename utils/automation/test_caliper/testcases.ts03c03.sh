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
#args
sTCIDPre=${1}
sTag1=${2}
sTCIDs=${3}
sCaliperCmd=${4}
sBenchTools=${5}
flLogCaliper=${6}
sOtherArgs=${7}

##########
#args correct
PureMarkSign sTCIDPre
sTCIDPre=${sTCIDPre}_TC_

sOtherArgs1=$(sed "s/^[ \t]*\(${g_reName}=\)/local \1/" <<< "${sOtherArgs}")
eval "${sOtherArgs1}"
CheckVarDefined varSucc "${sOtherArgs}"
CheckVarDefined varFail "${sOtherArgs}"
CheckVarDefined sArchTarget "${sOtherArgs}"
CheckVarDefined sIPTarget "${sOtherArgs}"

##########
#variables
nErrs=0
sFind=":[ \t]*[A-Za-z_]\+[0-9A-Za-z_]*[ \t]\+is already build"

##########
${sCaliperCmd} 2>&1 |tee ${flLogCaliper}

##########
grep -q "${sFind}" "${flLogCaliper}"
CheckCondition "$?" "-ne" 0 ${sTCIDPre}03 "${sTag1}" sTCIDs all "${varSucc}" "${varFail}"
let nErrs+=$?

##########
exit ${nErrs}

#####################

