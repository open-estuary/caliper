#!/bin/bash

g_FILE=$(basename ${0})
. $(dirname ${0})/${g_FILE%%.*}.common

g_drPro=$(Pure2Dir "${PWD}" "$(dirname ${0})")
g_FILE=$(basename ${0})

#####################
g_flListBenToolsCfg=$(FillPathByFind "${g_drTCs}" "${g_flListBenToolsCfg}")
PreEnOrDisAble

#bench tools
EnableAll "${g_ableType}" "${g_flListBenToolsCfg}"

###########
#machine
InitFile "${g_drMCfg}/client_config.cfg" g_a g_aN g_aV
if false && [ -f "${g_drMCfg}/email_config.cfg" ]; then
    cp /etc/caliper/config/email_config.cfg ${g_drMCfg}/.
fi
InitFile "${g_drMCfg}/email_config.cfg" g_aEmail g_aEmailN g_aEmailV

f1=${g_drTCs}/server/sysbench/sysbench_run.cfg
grep -q "\(^[ \t]*\|/\)sysbench.sh ${g_dbUsr} [\"\']\{0,1\}${g_dbPwd}[\"\']\{0,1\}[ \t]*\(;\|$\)" "${f1}"
if [ $? -ne 0 ]; then
    g_dbPwd=$(echo "${g_dbPwd}" |sed 's#/#\\/#g')
    sed -i "s/\(^[ \t]*\|\/\)sysbench.sh[ \t]\+[a-zA-Z_]\+[a-zA-Z_0-9]*[ \t]\+[\"\']\{0,1\}.\+[\"\']\{0,1\}[ \t]*\(;\|$\)/\1sysbench.sh ${g_dbUsr} \'${g_dbPwd}\'\2/g" "${f1}"
    if [ $? -eq 0 ]; then
        printf "%s[%3s]%5s: update [${f1}] db login info\n" "${FUNCNAME[0]}" ${LINENO} "Info"
    fi
fi

#caliper\benchmarks\315.sysbench\sysbench.sh

#####################

