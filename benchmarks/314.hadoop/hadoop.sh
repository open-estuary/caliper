#!/bin/bash

#it run very long time.
#if we need debug any issue, or the issue reproducibility random,
#we can add it to the corresponding position.
#set -x

#hdfs_tmp=/tmp/hadoop-${USER}

HADOOP_DIR=$PWD/hadoop
HADOOP_CONF=$HADOOP_DIR/etc/hadoop
HADOOP_BIN=$HADOOP_DIR/bin
HADOOP_SERVICE=$HADOOP_DIR/sbin

SPARK_DIR=$PWD/spark

HIBENCH_DIR=$PWD/hibench
HIBENCH_CONF=$HIBENCH_DIR/conf
HIBENCH_BIN=$HIBENCH_DIR/bin
HIBENCH_OUTPUT=$HIBENCH_DIR/report

##### set the ssh no-passwd login #####
if [ ! -f ~/.ssh/*.pub ]; then
    ./generate_keys.sh
fi
sKeyPub=$(cat ~/.ssh/id_*.pub)
f0=~/.ssh/authorized_keys
##Avoid duplication to add
grep -q "${sKeyPub}" ${f0} 2>/dev/null
if [ $? -ne 0 ]; then
    cat ~/.ssh/*.pub >>${f0}
fi

##############################
#tmp log dir
drTmpHadoop=/mnt/tmpLogCaliper/hadoop
drTmpHadoop=/mnt/hadoop
grep -q "${drTmpHadoop}" <<< "${HADOOP_TMP}"
if [ $? -ne 0 ]; then
    export HADOOP_TMP=${drTmpHadoop}
fi
rm -rf "${drTmpHadoop}"
mkdir -p "${drTmpHadoop}"

##############################
#JAVA_HOME
java_loc=$(find /usr/lib/jvm -name 'java-*-openjdk*' |sed -n "1p")
printf "%s[%3s]%5s: ${java_loc}\n" "${FUNCNAME[0]}" ${LINENO} "Info"

export JAVA_HOME=$java_loc
export CLASSPATH=.:$JAVA_HOME/lib:$JAVA_HOME/jre/lib

grep -qF "export JAVA_HOME=$java_loc" $HADOOP_CONF/hadoop-env.sh
if [ $? -ne 0 ]; then
    echo "export JAVA_HOME=$java_loc" >> $HADOOP_CONF/hadoop-env.sh
fi

##############################
pushd $HADOOP_DIR
/usr/bin/expect  << EOF
    set timeout  300
    spawn $HADOOP_SERVICE/stop-all.sh
    expect {
        -re {connecting \(yes/no\)\?} {
            send "yes\n"
            exp_continue
        }
        eof
    }
EOF

$HADOOP_BIN/hdfs namenode -format

##############################
bOK1=false
nMax1=2
n1=0
##while for fixed the "SecondaryNameNode" not started.
while [ ${n1} -lt ${nMax1} ]; do
    sInfo1=$(/usr/bin/expect  << EOF

    set timeout  300
    spawn $HADOOP_SERVICE/start-dfs.sh
    expect {
        -re {connecting \(yes/no\)\?} {
            send "yes\n"
            exp_continue
        }
        eof
    }
EOF
    )
    hdfs_jps=$(jps)
    echo "${hdfs_jps}" |grep -iqw "SecondaryNameNode"
    if [ $? -eq 0 ]; then
        echo "${hdfs_jps}" |grep -iqw "NameNode"
        if [ $? -eq 0 ]; then
            echo "${hdfs_jps}" |grep -iqw "DataNode"
            if [ $? -eq 0 ]; then
                bOK1=true
                break
            fi
        fi
    fi

    let n1+=1
done

printf "%s[%3s]%5s: while [ ${n1} -lt ${nMax1} ] ${sInfo1}\n${hdfs_jps}\n" "${FUNCNAME[0]}" ${LINENO} "Info"
if ! ${bOK1}; then
    printf "%s[%3s]%5s: Java Proc [NameNode SecondaryNameNode DataNode] have failed\n" "${FUNCNAME[0]}" ${LINENO} "Error" 1>&2
    exit 1
fi

/usr/bin/expect  << EOF
    set timeout  300
    spawn $HADOOP_SERVICE/start-yarn.sh
    expect {
        -re {connecting \(yes/no\)\?} {
            send "yes\n"
            exp_continue
        }
        eof
    }
EOF

yarn_jps=$(jps)
yarn_suc=$(echo $yarn_jps | grep -w 'NodeManager')
yarn_suc1=$(echo $yarn_jps | grep -w 'ResourceManager')
if [ "$yarn_suc"x != ""x -a "$yarn_suc1"x != ""x ]; then
    echo 'yarn run successfully'
else 
    echo 'yarn set up failed'
    exit 1
fi

popd

##############################
SetKeyBlankValue()
{
    local sKey1=${1}
    local sVal1=${2}
    local varTxt=${3}
    local varNDo=${4}

    sKey1=$(sed "s@\([./]\)@\\\\\1@g" <<< "${sKey1}")
    sVal1=$(sed "s@\([./]\)@\\\\\1@g" <<< "${sVal1}")

    eval local sTxt1=\${${varTxt}}

    grep -q "^[ 	]*${sKey1}[ 	]\+" <<< "${sTxt1}"
    if [ $? -ne 0 ]; then
        printf "%s[%3d]%s[%3d]%5s: [${sKey1}] not found\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Error"
        return 1
    fi

    #f1="/root/caliper/binary/arm_64/hadoop/hibench/conf/99-user_defined_properties.conf"
    #grep "hibench.hadoop.home		/root/caliper/binary/arm_64/hadoop/hadoop" "${f1}"
    grep -q "^[ 	]*${sKey1}[ 	]\+${sVal1}" <<< "${sTxt1}"
    if [ $? -ne 0 ]; then
        sTxt1=$(sed "/^[ \t]*${sKey1}[ \t]\+/{s/^\([ \t]*${sKey1}[ \t]\+\).*\$/\1${sVal1}/}" <<< "${sTxt1}")
        eval ${varTxt}=\${sTxt1}
        eval let ${varNDo}+=1
    fi

    return 0
}

AbleKey()
{
    local sKey1=${1}
    local bAble=${2}
    local varTxt=${3}
    local varNDo=${4}

    sKey1=$(sed "s@\([./]\)@\\\\\1@g" <<< "${sKey1}")

    eval local sTxt1=\${${varTxt}}

    grep -q "^[ 	#]*${sKey1}\([ 	#;]\+\|\$\)" <<< "${sTxt1}"
    if [ $? -ne 0 ]; then
        printf "%s[%3d]%s[%3d]%5s: [${sKey1}] not found\n" "${FUNCNAME[1]}" "${BASH_LINENO[0]}" "${FUNCNAME[0]}" ${LINENO} "Error"
        return 1
    fi

    if [ "${bAble}" == "true" ]; then
        grep -q "^[ 	]*#[ 	]*${sKey1}\([ 	#;]\+\|\$\)" <<< "${sTxt1}"
        if [ $? -eq 0 ]; then
            sTxt1=$(sed "/^[ \t]*#[ \t]*${sKey1}\([ \t#;]\+\|\$\)/{s/^\([ \t]*\)#\([ \t]*\)\(${sKey1}\)\([ \t#;]\+\|\$\)/\1\2\3\4/}" <<< "${sTxt1}")
            eval ${varTxt}=\${sTxt1}
            eval let ${varNDo}+=1
        fi
    else
        grep -q "^[ 	]*${sKey1}\([ 	#;]\+\|\$\)" <<< "${sTxt1}"
        if [ $? -eq 0 ]; then
            sTxt1=$(sed "/^[ \t]*${sKey1}\([ \t#;]\+\|\$\)/{s/^\([ \t]*\)\(${sKey1}\)\([ \t#;]\+\|\$\)/\1#\2\3/}" <<< "${sTxt1}")
            eval ${varTxt}=\${sTxt1}
            eval let ${varNDo}+=1
        fi
    fi

    return 0
}

##############################
#set config
HIBENCH_LAN_API=$HIBENCH_CONF/languages.lst
sed -i "s@^\([ \t]*\)\(spark/\)@\1#\2@" "${HIBENCH_LAN_API}"

#########
HIBENCH_BENCH_LIST=$HIBENCH_CONF/benchmarks.lst
flCfgH=${HIBENCH_BENCH_LIST}
sFlCfgH=$(cat "${flCfgH}")
nModify=0
AbleKey "aggregation" true sFlCfgH nModify
AbleKey "join" true sFlCfgH nModify
AbleKey "pagerank" true sFlCfgH nModify
AbleKey "scan" true sFlCfgH nModify
AbleKey "nutchindexing" false sFlCfgH nModify

if [ ${nModify} -gt 0 ]; then
    echo "${sFlCfgH}" > "${flCfgH}"
fi

#########
flCfgH=${HIBENCH_CONF}/99-user_defined_properties.conf
cp "${flCfgH}.template" "${flCfgH}"
sFlCfgH=$(cat "${flCfgH}")

nModify=0
SetKeyBlankValue "hibench.hadoop.home" "${HADOOP_DIR}" sFlCfgH nModify
SetKeyBlankValue "hibench.spark.home" "${SPARK_DIR}" sFlCfgH nModify
SetKeyBlankValue "hibench.hdfs.master" "hdfs://localhost:9000" sFlCfgH nModify
SetKeyBlankValue "hibench.default.map.parallelism" "2" sFlCfgH nModify
SetKeyBlankValue "hibench.default.shuffle.parallelism" "1" sFlCfgH nModify
#?s/ 4 / 2 /g
SetKeyBlankValue "hibench.yarn.executor.num" "2" sFlCfgH nModify
SetKeyBlankValue "hibench.yarn.executor.cores" "2" sFlCfgH nModify

AbleKey "hibench.spark.master" false sFlCfgH nModify
AbleKey "hibench.spark.version" true sFlCfgH nModify

if [ ${nModify} -gt 0 ]; then
    echo "${sFlCfgH}" > "${flCfgH}"
fi

#########
flCfgH=$HIBENCH_CONF/10-data-scale-profile.conf
sFlCfgH=$(cat "${flCfgH}")

nModify=0
SetKeyBlankValue "hibench.dfsioe.large.read.number_of_files" 40 sFlCfgH nModify
SetKeyBlankValue "hibench.dfsioe.large.read.file_size" 2048 sFlCfgH nModify
SetKeyBlankValue "hibench.dfsioe.large.write.number_of_files" 40 sFlCfgH nModify
SetKeyBlankValue "hibench.dfsioe.large.write.file_size" 2048 sFlCfgH nModify

if [ ${nModify} -gt 0 ]; then
    echo "${sFlCfgH}" > "${flCfgH}"
fi

##############################

############## start hibench testing ##############
pushd $HIBENCH_DIR
    RESULT=$HIBENCH_DIR/report/hibench.report
    if [ -f $RESULT ]; then
        rm -fr $RESULT
    fi
    ./bin/run-all.sh
    if [ -f $RESULT ]; then
        cat $RESULT
    else
        echo 'The Hibench test has not generate the report, runs error.'
        exit 
    fi
popd

############## stop hadoop service ##############
pushd $HADOOP_DIR
  $HADOOP_SERVICE/stop-yarn.sh
  if [ $? -ne 0 ]; then 
      echo 'stop yarn service failed'
  fi
  $HADOOP_SERVICE/stop-dfs.sh
  if [ $? -ne 0 ]; then 
      echo 'stop hdfs service failed'
  fi
popd
 
