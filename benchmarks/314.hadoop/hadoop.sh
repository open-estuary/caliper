#!/bin/bash

#it run very long time.
#if we need debug any issue, or the issue reproducibility random,
#we can add it to the corresponding position.
#set -x

#hdfs_tmp=/tmp/hadoop-${USER}
. ~/.bashrc

echo  "$HADOOP_TMP  the hadoop tmp directory"

if [ -e  $HADOOP_TMP ] ; then 
rm -r  $HADOOP_TMP
fi

hdfs_tmp=$HADOOP_TMP

HADOOP_DIR=$PWD/hadoop
HADOOP_CONF=$HADOOP_DIR/etc/hadoop
HADOOP_BIN=$HADOOP_DIR/bin
HADOOP_SERVICE=$HADOOP_DIR/sbin

SPARK_DIR=$PWD/spark

HIBENCH_DIR=$PWD/hibench
HIBENCH_CONF=$HIBENCH_DIR/conf
HIBENCH_BIN=$HIBENCH_DIR/bin
HIBENCH_OUTPUT=$HIBENCH_DIR/report
HIBENCH_BENCH_LIST=$HIBENCH_CONF/benchmarks.lst
HIBENCH_LAN_API=$HIBENCH_CONF/languages.lst
HIBENCH_DATA_PROFILE=$HIBENCH_CONF/10-data-scale-profile.conf
sudo apt-get install expect -y

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

############## get JAVA_HOME which need to be used later ################


#Is java installed?
if ! hash java; then
    sudo apt-get -y install openjdk-7-jdk
    if [ $? -ne 0 ]; then
        printf "%s[%3s]%5s: install openjdk-7-jdk failed\n" "${FUNCNAME[0]}" ${LINENO} "Error" 1>&2
        exit 1
    fi
fi

#Get the java path
java_loc=$(find /usr/lib -name 'java-*-openjdk*' |sed -n "1p")
printf "%s[%3s]%5s: ${java_loc}\n" "${FUNCNAME[0]}" ${LINENO} "Info"

export JAVA_HOME=$java_loc
export CLASSPATH=.:$JAVA_HOME/lib:$JAVA_HOME/jre/lib

############# start the hadoop service ################
pushd $HADOOP_DIR
    pushd $HADOOP_CONF
    grep -q "export JAVA_HOME=$java_loc" $HADOOP_CONF/hadoop-env.sh
    if [ $? -ne 0 ]; then
        echo "export JAVA_HOME=$java_loc" >> $HADOOP_CONF/hadoop-env.sh
    fi
    popd

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

rm -fr $hdfs_tmp
$HADOOP_BIN/hdfs namenode -format

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

############## start hibench testing ################
pushd $HIBENCH_DIR
    sed -i 's/^spark/#spark/g'  $HIBENCH_LAN_API
    # benchmarks.lst modify
    sed -i 's/^nutchindexing/#nutchindexing/g' $HIBENCH_BENCH_LIST


    # modify 99-user_defined_properties.conf        
    pushd $HIBENCH_CONF
        cp 99-user_defined_properties.conf.template 99-user_defined_properties.conf
        USER_DEFINED_FILE=$HIBENCH_CONF/99-user_defined_properties.conf
#        hdfs_url="\/URL\/TO\/YOUR\/HDFS"
	 hdfs_url="hdfs\:\/\/HOSTNAME:HDFSPORT"
        hadoop_str="\/PATH\/TO\/YOUR\/HADOOP\/ROOT"
        hdfs_server="hdfs\:\/\/127\.0\.0\.1\:9000"
        spark_str="\/PATH\/TO\/YOUR\/SPARK\/ROOT"
	hadoop_dir=${HADOOP_DIR//\//\\\/}
    spark_dir=${SPARK_DIR//\//\\\/}
echo $hadoop_dir
        sed -i "s/$hadoop_str/$hadoop_dir/g"  $USER_DEFINED_FILE
        sed -i "s/$spark_str/$spark_dir/g" $USER_DEFINED_FILE
        sed -i "s/$hdfs_url/$hdfs_server/g" $USER_DEFINED_FILE
        sed -i 's/^hibench.spark.master/#hibench.spark.master/g' $USER_DEFINED_FILE
        sed -i 's/#hibench.spark.version/hibench.spark.version/g' $USER_DEFINED_FILE
        sed -i 's/ 4 / 2 /g' $USER_DEFINED_FILE
        sed -i '52,67s/12/2/g' $USER_DEFINED_FILE
        sed -i '52,67s/6/1/g'  $USER_DEFINED_FILE
	sed -i 's/.*hibench.dfsioe.large.read.number_of_files.*/hibench.dfsioe.large.read.number_of_files        40/'   $HIBENCH_DATA_PROFILE
        sed -i 's/.*hibench.dfsioe.large.read.file_size.*/hibench.dfsioe.large.read.file_size                  1024/'   $HIBENCH_DATA_PROFILE
        sed -i 's/.*hibench.dfsioe.large.write.number_of_files.*/hibench.dfsioe.large.write.number_of_files      40/'   $HIBENCH_DATA_PROFILE
        sed -i 's/.*hibench.dfsioe.large.write.file_size.*/hibench.dfsioe.large.write.file_size                1024/'   $HIBENCH_DATA_PROFILE

    popd

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


####### stop hadoop service ##########
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
 
