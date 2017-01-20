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
sSP='  '
printf "%3s${sSP}%-8s${sSP}%-15s${sSP}%-6s\n" NO SCENARIO ID STATUS > "${g_flLogStatusFmt}"

sInfo=$(grep "\[${g_sPKTSIDInLog}\]" "${g_flLogStatus}")
sInfo=$(sed "s#^.*\[${g_sPKTSIDInLog}\][ \t:]*##;s#^[ \t]*\[[ \t]*\([A-Za-z_]\+[A-Za-z_0-9]*\)[ \t]*\][ \t:]*\[[ \t]*\([A-Za-z_]\+[A-Za-z_0-9]*\)[ \t]*\][ \t:]*\$#\1\t\2#" <<< "${sInfo}")
#sInfo=$(sort -t'	' -k 1 <<< "${sInfo}")

n1=0
IFS=$'\n'; for sL1 in ${sInfo}; do IFS=${g_IFS0};
    let n1+=1
    #TS_01_TC_02A	Passed
    sID1=$(awk -F'\t' '{print $1}' <<< "${sL1}")
    sStatus=$(awk -F'\t' '{print $2}' <<< "${sL1}")
    scenario=$(awk -F'_TC_' '{print $1}' <<< "${sID1}")
    printf "%3s${sSP}%-8s${sSP}%-15s${sSP}%-6s\n" ${n1} "${scenario}" "${sID1}" "${sStatus}" >> "${g_flLogStatusFmt}"
IFS=$'\n'; done; IFS=${g_IFS0};

#####################

