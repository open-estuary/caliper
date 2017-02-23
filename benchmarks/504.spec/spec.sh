#!/bin/bash

typeTest=${1:-int}
nCopy=${2:-1}

drCur1=$(pwd)

flTar1=$(grep -i "spec.*cpu.*\.tar\.gz" <<< "$(ls -d *)")
if [ -z "${flTar1}" ]; then
    printf "%s[%3d]%s[%3d]%5s: spec package not exist in [${drCur1}]\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi
nRow1=$(wc -l <<< "${flTar1}")
if [ ${nRow1} -ne 1 ]; then
    printf "%s[%3d]%s[%3d]%5s: spec package exist multiple in [${drCur1}]\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

tar -xzf ${flTar1}
keyTar1=$(grep -oi "spec.*cpu" <<< "${flTar1}")
drs1=$(ls -d * |grep -vF "${flTar1}")
drSpec=$(grep -oi "spec.*cpu" <<< "${drs1}" |sed -n "1p")
if [ -z "${drSpec}" ]; then
    printf "%s[%3d]%s[%3d]%5s: unknow the spec folder\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi
cd ${drSpec}*

#####################
mkdir -p ~/tmp
flSpecLog=~/tmp/spec.log
. ./shrc
./bin/relocate
./bin/runspec -c lemon-2cpu.cfg ${typeTest} --rate ${nCopy} -n 1 --noreportable > "${flSpecLog}"

sLog1=$(grep -B3 "runspec finished" "${flSpecLog}")
key1="The log for this run is in"
sLog2=$(grep "${key1}" <<< "${sLog1}")
flBSLog=$(sed "s#^[ \t]*${key1}[ \t]\+##;s#[ \t]*\$##" <<< "${sLog2}")
cat "${flBSLog}"

#####################

