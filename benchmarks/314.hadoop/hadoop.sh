#!/bin/bash

#it run very long time.
#if we need debug any issue, or the issue reproducibility random,
#we can add it to the corresponding position.
#set -x

#hdfs_tmp=/tmp/hadoop-${USER}


if [[ "$#" -ne 2  ]] 
then
   echo -e "Usage : The number of command line arguments for hadoop.sh  should be 2 ,mount disk and mount point \n"
   echo -e   " hadoop.sh <disk> <mount_point> \n"
   echo -e  "Add the arguments in configuration/test_cases_cfg/common/hadoop/hadoop_run.cfg in command section as below \n"
   echo -e  "command = if [ -f hadoop_tar.gz ]; then tar -xvf hadoop_tar.gz; rm hadoop_tar.gz; fi; pushd hadoop; ./hadoop.sh <disk> <mount_point>; popd \n"
   echo -e "example: \n"
   echo -e "command = if [ -f hadoop_tar.gz ]; then tar -xvf hadoop_tar.gz; rm hadoop_tar.gz; fi; pushd hadoop; ./hadoop.sh /dev/sda /mnt/hadoop ; popd \n"

   exit 1
fi


disk=$( echo $1 | cut -d "/" -f 3 )

echo "Disk used for mounting is  $disk"


if [ `lsblk | grep -c "$disk"` == 0 ]
then
   echo "The disk specified for hadoop testing $1 is not vailable "
   exit 1
fi



if [ ! -d $2 ]
then
    echo -e "\nCreating Mount Partition for hadoop testing\n"
        sudo mkdir -p $2
        sudo chmod -R 775 $2
        sudo chown -R $USER:$USER $2
        sudo mount "$1" $2


        if [ $? -ne 0 ]
        then
       echo -e "\n$ERROR:Creating a Mount Path for Hadoop  testing Failed\n"
           exit 1
    fi
else
        if [ `mount -l | grep -c "$1 on $2"` == 0 ]
        then
            sudo mount "$1" $2
                if [ $? -ne 0 ]
                then
                echo -e "\n$ERROR:Creating a Mount Path for hadoop testing Failed\n"
                    exit 1
            fi
        fi
        echo -e "\nMount Partition for fio testing Already exits\n"
fi

HADOOP_TMP=$2
 

 grep HADOOP_TMP /etc/environment >> /dev/null


if [ $? = 0  ] 
 then 
        HADOOP_TMP=$(echo "$HADOOP_TMP" | sed 's/\//\\\//g')
        echo $HADOOP_TMP
        sed -i "s/^.*HADOOP_TMP.*/HADOOP_TMP=$HADOOP_TMP/"  /etc/environment
        echo " Replacing HADOOP_TMP variable value with $2  in /etc/environment "
else 

         echo "HADOOP_TMP=$HADOOP_TMP" >> /etc/environment 
         echo " Adding HADOOP_TMP variable $2 in /etc/environment "
fi


. ~/.bashrc
. /etc/environment


echo  "$HADOOP_TMP  the hadoop tmp directory for testing"

if [ -e  $HADOOP_TMP ] ; then 
rm -r  $HADOOP_TMP/dfs
fi


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
        sed -i 's/.*hibench.dfsioe.large.read.file_size.*/hibench.dfsioe.large.read.file_size                  2048/'   $HIBENCH_DATA_PROFILE
        sed -i 's/.*hibench.dfsioe.large.write.number_of_files.*/hibench.dfsioe.large.write.number_of_files      40/'   $HIBENCH_DATA_PROFILE
        sed -i 's/.*hibench.dfsioe.large.write.file_size.*/hibench.dfsioe.large.write.file_size                2048/'   $HIBENCH_DATA_PROFILE

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
 
