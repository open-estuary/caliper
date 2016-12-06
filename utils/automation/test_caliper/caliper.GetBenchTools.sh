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
g_flListBenToolsCfg=$(FillPathByFind "${g_drTCs}" "${g_flListBenToolsCfg}")

#BenchTools
sKeyMark=${1}

sKeysEnable=
sKeysDisable=
IFS=$'\n'; for f1 in ${g_flListBenToolsCfg}; do IFS=${g_IFS0};
    sKeysEnable=${sKeysEnable}$'\n'$(grep "^[ \t]*\[[a-zA-Z_]\+[a-zA-Z_0-9]*\]" "${f1}")
    sKeysDisable=${sKeysDisable}$'\n'$(grep "^[ \t]*#[ \t]*\[[a-zA-Z_]\+[a-zA-Z_0-9]*\]" "${f1}" |sed "s/^[ \t]*#[ \t]*//;")
IFS=$'\n'; done; IFS=${g_IFS0};

PureMarkSign sKeysEnable true
PureMarkSign sKeysDisable true

sKeysEnable=$(tr '\n' ',' <<< "${sKeysEnable}")
sKeysDisable=$(tr '\n' ',' <<< "${sKeysDisable}")

printf "%s[%3d]%5s: ${sKeyMark}: ${sKeysEnable}\n" "${FUNCNAME[0]}" ${LINENO} "Info"
printf "%s[%3d]%5s: ${sKeyMark}: #${sKeysDisable}\n" "${FUNCNAME[0]}" ${LINENO} "Info"

#####################

