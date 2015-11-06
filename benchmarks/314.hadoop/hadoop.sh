#!/bin/bash

#set -x

user=$(echo $USER)
hdfs_tmp=/tmp/hadoop-$user

HADOOP_DIR=$PWD/hadoop
HADOOP_CONF=$HADOOP_DIR/etc/hadoop
HADOOP_BIN=$HADOOP_DIR/bin
HADOOP_SERVICE=$HADOOP_DIR/sbin

HIBENCH_DIR=$PWD/hibench
HIBENCH_CONF=$HIBENCH_DIR/conf
HIBENCH_BIN=$HIBENCH_DIR/bin
HIBENCH_OUTPUT=$HIBENCH_DIR/report
HIBENCH_BENCH_LIST=$HIBENCH_CONF/benchmarks.lst
HIBENCH_LAN_API=$HIBENCH_CONF/languages.lst

##### set the ssh no-passwd login #####
if [ ! -f ~/.ssh/*.pub ]; then
    ./generate_keys.sh
fi
public_key=$(cat ~/.ssh/*.pub)
echo $public_key >> ~/.ssh/authorized_keys

############## get JAVA_HOME which need to be used later ################
java_version=`java -version 2>tmp_001.txt && awk '/java/{print $0}' tmp_001.txt`
if [ "$java_version"x = ""x ]; then
    sudo apt-get install openjdk-7-jdk -y
    if [ $? -ne 0 ]; then
        echo 'Install openjdk-7-jdk error'
    fi
    java_location=$(find /usr/lib -name 'java-*-openjdk*')
    java_loc=$(echo $java_location | awk '{print $1}')
    echo "java install location is $java_loc"

    echo "export JAVA_HOME=$java_loc" >> /etc/profile
    echo 'export JAVA_JRE=$JAVA_HOME/jre'  >> /etc/profile
    echo 'CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH'  >> /etc/profile 
    source /etc/profile
elif [ "$(whereis java)"x != ""x ]; then 
    java_location=$(find /usr/lib -name 'java-*-openjdk*')
    java_loc=$(echo $java_location | awk '{print $1}')
    echo "java install location is $java_loc"

    echo "export JAVA_HOME=$java_loc" >> /etc/profile
    echo 'export JAVA_JRE=$JAVA_HOME/jre'  >> /etc/profile
    echo 'CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH'  >> /etc/profile 
    source /etc/profile
else
    # java is installed 
    flag=0
    sys_path=(${PATH//:/ })
    
    for i in ${sys_path[@]}
    do
        tmp=$(echo $i | grep 'java' | grep 'bin' | grep -v 'jre')
        if [ "$tmp"x != ""x ]; then
            flag=1
            java_loc=${i%bin}
        fi
        break
    done
    if [ $flag -ne 1 ]; then
        echo 'You have installed java, but you still need to configure the java
        location in the /etc/profile or ~/.bashrc'
        exit
    fi
fi

############# start the hadoop service ################
pushd $HADOOP_DIR
  pushd $HADOOP_CONF
    echo "export JAVA_HOME=$java_loc" >> $HADOOP_CONF/hadoop-env.sh
  popd
  $HADOOP_SERVICE/stop-dfs.sh
  rm -fr $hdfs_tmp
  $HADOOP_BIN/hdfs namenode -format
  $HADOOP_SERVICE/start-dfs.sh
  hdfs_jps=$(jps)
  if [ "$(echo $hdfs_jps | grep -w 'SecondaryNameNode')"x != ""x ]; then
    if [ "$(echo $hdfs_jps | grep -w 'DataNode')"x != ""x ]; then
      if [ "$(echo $hdfs_jps | grep -w 'NameNode')"x != ""x ]; then
      	echo 'hdfs run successfully'
      else
	echo 'Namenode setup error'
	exit
      fi
    else
        echo 'DataNode setup error'
	exit
    fi
  else
    echo 'SecondaryNameNode setup error'
    exit
  fi

  $HADOOP_SERVICE/start-yarn.sh
  yarn_jps=$(jps)
  yarn_suc=$(echo $yarn_jps | grep -w 'NodeManager')
  yarn_suc1=$(echo $yarn_jps | grep -w 'ResourceManager')
  if [ "$yarn_suc"x != ""x -a "$yarn_suc1"x != ""x ]; then
      echo 'yarn run successfully'
  else 
      echo 'yarn set up failed'
      exit
  fi
popd

############## start hibench testing ################
pushd $HIBENCH_DIR
    sed -i 's/^spark/#spark/g'  $HIBENCH_LAN_API
    # benchmarks.lst modify
    sed -i 's/^aggregation/#aggregation/g' $HIBENCH_BENCH_LIST
    sed -i 's/^join/#join/g' $HIBENCH_BENCH_LIST
    sed -i 's/^pagerank/#pagerank/g' $HIBENCH_BENCH_LIST
    sed -i 's/^scan/#scan/g' $HIBENCH_BENCH_LIST
    sed -i 's/^nutchindexing/#nutchindexing/g' $HIBENCH_BENCH_LIST
    # modify 99-user_defined_properties.conf        
    pushd $HIBENCH_CONF
        cp 99-user_defined_properties.conf.template 99-user_defined_properties.conf
        USER_DEFINED_FILE=$HIBENCH_CONF/99-user_defined_properties.conf
        hdfs_url="\/URL\/TO\/YOUR\/HDFS"
        hadoop_str="\/PATH\/TO\/YOUR\/HADOOP\/ROOT"
        hdfs_server="hdfs\:\/\/127\.0\.0\.1\:9000"
	hadoop_dir=${HADOOP_DIR//\//\\\/}
echo $hadoop_dir
        sed -i "s/$hadoop_str/$hadoop_dir/g"  $USER_DEFINED_FILE
        sed -i "s/$hdfs_url/$hdfs_server/g" $USER_DEFINED_FILE
        sed -i 's/^hibench.spark/#hibench.spark/g' $USER_DEFINED_FILE
        sed -i 's/4/2/g' $USER_DEFINED_FILE
        sed -i '52,67s/12/2/g' $USER_DEFINED_FILE
        sed -i '52,67s/6/1/g'  $USER_DEFINED_FILE
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
 
