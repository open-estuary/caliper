#!/bin/bash
#############################################################################
#date: 2016/10/10 - 2016/11/25
#author: Bel.He(Zhongyan.He)
#function: Automatic test caliper(options)
#introduction: This is the main script, you need set "caliper.cfg" main
#  fields and Set the "testcases.main.cfg" some fields, then this script
#  will read configuration from "testcases.main.cfg", and modify the
#  "caliper.cfg" some fields and auto run caliper
#############################################################################

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
sFMainCfg=$(cat "${g_drPro}/${g_flMainCfg}")
flSetCaliperCfgProCfg="${g_drProSetCaliperCfg}/caliper.cfg"
nErrsMain=0
nMachine=0
nBP=0
nIDsTotal=0
export g_nSucc=0
export g_nFail=0
export g_drsWReport=
declare -a nBackPros

#Get the all line number of test cases
nL1=$(SectLineNosPairs 0 '^[ \t]*'"\[.*\]" sFMainCfg '^[ \t#]*\[.*\]')
#printf "%s[%3d]%5s: ${nL1}\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flBaseLog}.log
IFS=$'\n'; for nL2 in ${nL1}; do IFS=${g_IFS0};
    #Get the value from config file
    ###########
    #The title of test case information
    sSect=$(sed -n "${nL2}p" <<< "${sFMainCfg}")
    sTitle=$(sed -n "1p" <<< "${sSect}")

    #The body of test case information
    sSect=$(sed -n "2,\$p" <<< "${sSect}" |grep -v "^[ \t]*#")
    runMode=
    eval "${sSect}"
    sTag=${tag}
    sIPTarget=${targetIP}
    sPlatformName=${platformName}
    sIDs=${IDs}
    sTools=${tools}
    sCaliperCmd=${caliperCmd}
    sRunMode=${runMode}
    sEntryProgram=${entryProgram}

    ##########
    #amend arguments
    if [ -z "${sRunMode}" ]; then
        sRunMode=foreground
    fi
    #about arguments
    CountLineFields ',' "${sIDs}" nField
    let nIDsTotal+=nField

    if [ "${stOutputDirCollect}" == "start" ]; then
        g_drsWReport=
        stOutputDirCollect=doing
    fi

    ######
    echo |tee -a ${g_flBaseLog}.log
    sRun1="--==>>++ [${sCaliperCmd}]"
    printf "%s[%3d]%5s: $(date '+%Y%m%d_%H%M%S_%N') ${sTitle} [${sIPTarget}] ${sRun1}\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flBaseLog}.log

    ######
    #caliper config set
    sCmdName=$(grep "\(^\|^[ \t]*[^#]\)[ \t]*\<caliper\>" <<< "${sCaliperCmd}")
    if [ -z "${sCmdName}" ]; then
        sCmdName=$(sed "s/^[ \t]*\$/d" <<< "${sCaliperCmd}" |sed -n "\$p")
        if [ -z "${sCmdName}" ]; then
            printf "%s[%3d]%5s: [${sCaliperCmd}] is empty\n" "${FUNCNAME[0]}" ${LINENO} "Error" |tee -a ${g_flBaseLog}.log
            exit 1
        fi
    fi
    nRow1=$(wc -l <<< "${sCmdName}")
    if [ ${nRow1} -ne 1 ]; then
        printf "%s[%3d]%5s: [${sCmdName}] not one line\n" "${FUNCNAME[0]}" ${LINENO} "Error" |tee -a ${g_flBaseLog}.log
        exit 1
    fi

    CheckOption f "${sCmdName}"
    if [ $? -eq 0 ]; then
        drOutputFrom=$(sed "s/^[ \t#]*[A-Za-z_]\+[0-9A-Za-z_]*[ \t]\+-[A-Za-eg-z]*f[ \t]\+\(.*\)[ \t]*\$/\1/" <<< "${sCmdName}")
    else
        drOutputFrom=configuration
    fi
    
    drPathOutput="${g_drBase}/${drOutputFrom}"
    if [ ! -d "${drPathOutput}" ]; then
        drPathOutput="${g_drBase}/configuration"
    fi

    sTxtCfg=$(cat ${flSetCaliperCfgProCfg})
    sTxtModify=

    SetSetCaliperCfgCfg g_drBase "${drPathOutput}" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
    SetSetCaliperCfgCfg g_ipTarget "${sIPTarget}" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
    if [ -z "${sTools}" ]; then
        SetSetCaliperCfgCfg g_ableType "enMost" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
        SetSetCaliperCfgCfg g_disablePart "" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
    else
        sAble="\"
        $(sed 's/^[ \t#]\+//;s/[ \t]*,[ \t#]*/\n/g;s/[ \t,]\+$//' <<< "${sTools}")
        \""
        grep -q "^[ \t]*#" <<< "${sTools}"
        if [ $? -eq 0 ]; then
            SetSetCaliperCfgCfg g_ableType "enMost" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
            SetSetCaliperCfgCfg g_disablePart "${sAble}" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
        else
            SetSetCaliperCfgCfg g_ableType "disMost" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
            SetSetCaliperCfgCfg g_enablePart "${sAble}" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
        fi
    fi

    SetSetCaliperCfgCfg g_targetName "${sPlatformName}" "sTxtModify" "sTxtCfg" "${flSetCaliperCfgProCfg}" true
    if [ -n "${sTxtModify}" ]; then
        echo "${sTxtCfg}" >${flSetCaliperCfgProCfg}
        printf "%s[%3d]%5s: [${flSetCaliperCfgProCfg}] modify:${sTxtModify}\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flBaseLog}.log
    fi
    #echo "${sTxtCfg}" >~/tmp/a.cfg
    #exit 1
    ###
    #to set caliper config
    ${g_drProSetCaliperCfg}/caliper.sh |tee -a ${g_flBaseLog}.log
    sToolsCfg=$(${g_drProSetCaliperCfg}/caliper.GetBenchTools.sh BenchToolsMark)
    sToolsCfg=$(grep "[: \t]\+BenchToolsMark[ \t]*:" <<< "${sToolsCfg}" |sed "s/^.*[: \t]\+BenchToolsMark[ \t]*:[ \t]*//")
    sToolsCfg=$(grep -v "^[ \t]*#" <<< "${sToolsCfg}")

    ######
    #caliper output log
    sCmdName=$(sed "s#^[ \t]\+##;s#[ \t]\+\$##;s#_#__#g;s# \+#_#g" <<<"${sCmdName}" |tr -d "\012")

    ######
    n1=0
    flLogCaliper="${g_flBaseLog}.${sCmdName}.$(printf "%02d" ${n1})"
    while [ -e "${flLogCaliper}" ]; do
        let n1+=1
        flLogCaliper="${g_flBaseLog}.${sCmdName}.$(printf "%02d" ${n1})"
    done
    printf "%s[%3d]%5s: caliper log file: [${flLogCaliper}]\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flBaseLog}.log

    ######
    #target info
    #sArchTarget=$(ExpectExecCmd "ssh root@${sIPTarget} "'"lscpu |grep \"^\[ \t\]*Architecture:\" |sed \"s/^\[ \t\]*Architecture:\[ \t\]*//\""' |sed "s/[ \t\r]\+\$//")
    sInfo1=$(ExpectExecCmd "ssh -o ConnectTimeout=60 root@${sIPTarget} lscpu")
    sArchTarget=$(grep "^[ \t]*Architecture:" <<< "${sInfo1}")
    if [ $? -ne 0 ]; then
        printf "%s[%3d]%5s: ssh -o ConnectTimeout=60 root@${sIPTarget} lscpu [${sInfo1}] can not get the machine Architecture\n" "${FUNCNAME[0]}" ${LINENO} "Error" |tee -a ${g_flBaseLog}.log
        nMachine=0
        let nErrsMain+=1
        exit 1
    fi
    sArchTarget=$(sed "s/^[ \t]*Architecture:[ \t]*//" <<< "${sArchTarget}" |sed "s/[ \t\r]\+\$//")
    sOtherArgs="
        varSucc=g_nSucc
        varFail=g_nFail
        sArchTarget='${sArchTarget}'
        sIPTarget='${sIPTarget}'
    "
    ###
    #run the test script
    sPro=:
    if [ -f "${g_drPro}/${sEntryProgram}" ]; then
        sPro=${g_drPro}/${sEntryProgram}
    elif hash "${sEntryProgram}"; then
        sPro=${sEntryProgram}
    else
        sPro=:
        printf "%s[%3d]%5s: ${sEntryProgram} not defined\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flBaseLog}.log
        exit 1
    fi
    printf "%s[%3d]%5s: ${sPro} -- [${sIPTarget}]\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flBaseLog}.log
    case "${sRunMode}" in
    foreground)
        nMachine=0
        ${sPro} "${sTitle}" "${sTag}" "${sIDs}" "${sCaliperCmd}" "${sToolsCfg}" "${flLogCaliper}" "${sOtherArgs}"
        let nErrsMain+=$?
        ;;
    background)
        let nMachine+=1
        ${sPro} "${sTitle}" "${sTag}" "${sIDs}" "${sCaliperCmd}" "${sToolsCfg}" "${flLogCaliper}" "${sOtherArgs}" &
        nBackPros[${nBP}]=${!}
        let nBP+=1
        sleep 3
        ;;
    esac
IFS=$'\n'; done; IFS=${g_IFS0};

n1=0
while [ ${n1} -lt ${#nBackPros} ]; do
    wait ${nBackPros[${n1}]}
    let nErrsMain+=$?
    let n1+=1
done

printf "%s[%3d]%5s: ${nIDsTotal} test cases ${g_success}[${g_nSucc}] ${g_failure}[${g_nFail}]\n" "${FUNCNAME[0]}" ${LINENO} "Info" |tee -a ${g_flLogStatus}
if [ ${nErrsMain} -ne 0 ]; then
    printf "%s[%3d]%5s: result have error [${nErrsMain}]\n" "${FUNCNAME[0]}" ${LINENO} "Error" |tee -a ${g_flLogStatus}
fi

let nIDsTotal1=g_nSucc+g_nFail
if [ ${nIDsTotal} -ne ${nIDsTotal1} ]; then
    let nIDsTotal2=nIDsTotal-nIDsTotal1
    printf "%s[%3d]%5s: ${nIDsTotal2} test cases not test\n" "${FUNCNAME[0]}" ${LINENO} "Error" |tee -a ${g_flLogStatus}
fi

${g_drPro}/${g_fln%%.*}.FormatLog.sh

#####################

