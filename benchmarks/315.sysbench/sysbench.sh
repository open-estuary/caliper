#!/bin/bash
set -x
sysbench_dir=sysbench-0.5
cpu_num=$(grep 'processor' /proc/cpuinfo |sort |uniq |wc -l)

db_driver=mysql
: ${mysql_table_engine:=$1}
: ${mysql_table_engine:=innodb}
: ${oltp_table_size:=$2}
: ${oltp_table_size:=100000}
: ${oltp_tables_count:=$3}
: ${oltp_tables_count:=8}
#: ${num_threads:=$4}
: ${num_threads:=$((cpu_num*2))}
: ${mysql_host:=$5}
: ${mysql_host:=localhost}
: ${mysql_port:=$6}
: ${mysql_port:=33306}
: ${mysql_user:=$7}
: ${mysql_user:=root}
: ${mysql_password:=$8}
: ${mysql_password:=123456}
: ${db_name:=$9}
: ${db_name:=sbtest}
: ${max_requests:=$10}
: ${max_requests:=10000}
test_name="$PWD/sysbench-0.5/sysbench/tests/db/oltp.lua"

sudo apt-get install libtool -y
sudo apt-get install autoconf -y
sudo apt-get install automake -y

exists=$(ps -aux | grep 'mysqld')
if [ "$exists"x = ""x ]; then
    echo 'The mysql server has not been installed'
    exit
fi

sudo apt-get install libmysqlclient-dev -y
sudo apt-get install libmysqld-dev -y

sudo apt-get install bzr -y

if [ ! -d $sysbench_dir ]; then
  bzr branch lp:~sysbench-developers/sysbench/0.5 $sysbench_dir
  if [ $? -ne 0 ]; then
    echo 'Download the sysbench failed'
    exit
  fi
fi

mysql_location=$(whereis mysql)

declare -a mysql_loc
read -a mysql_loc <<< $(echo $mysql_location)

for j in ${mysql_loc[@]}
do
echo $j
done

for i in ${mysql_loc[@]}
do
   echo $i
    tmp=$(echo $i | grep '\/lib\/mysql')
    tmp1=$(echo $i | grep '\/include\/mysql')
    if [ "$tmp"x != ""x ]; then
        mysql_lib=$tmp
    elif [ "$tmp1"x != ""x ]; then
        mysql_include=$tmp1
    fi
done

if [ "$mysql_lib"x = ""x || "$mysql_include"x = ""x ]; then
    echo 'mysql has not been installed right'
    exit
fi

if [ ! -d $sysbench_dir ]; then
    echo 'sysbench has not been download completely'
    exit
fi

export PATH=$PATH:/usr/local

pushd $sysbench_dir
  prefix=/usr/local/sysbench
  ./autogen.sh
  ./configure --prefix=$prefix --with-mysql-includes=$mysql_include
  --with0mysql-libs=$mysql_lib
  make 
  make install
popd

sudo apt-get install expect -y
if [ $? -ne 0 ]; then 
    echo "install expect failed"
    exit
fi

# create $db_name in the databases
./mysql.sh $mysql_user $mysql_passwd $db_name

echo $num_threads
# prepare the test data
$sysbench_dir/sysbench/sysbench \
  --db-driver=mysql \
  --mysql-table-engine=innodb \
  --oltp-table-size=$oltp_table_size \
  --oltp-tables-count=$oltp_tables_count \
  --num-threads=$num_threads \
  --mysql-host=$mysql_host \
  --mysql-user=$mysql_user \
  --mysql-password=$mysql_password \
  --max-requests=$max_requests\
  --test=$test_name \
  prepare

if [ $? -ne 0 ]; then
    echo 'Prepare the oltp test data failed'
    exit
fi

# do the oltp test
 $sysbench_dir/sysbench/sysbench \
  --db-driver=mysql \
  --mysql-table-engine=innodb \
  --oltp-table-size=$oltp_table_size \
  --oltp-tables-count=$oltp_tables_count \
  --num-threads=$num_threads \
  --mysql-host=$mysql_host \
  --mysql-user=$mysql_user \
  --mysql-password=$mysql_password \
  --max-requests=$max_requests\
  --test=$test_name \
  run

if [ $? -ne 0 ]; then
    echo 'Run the oltp test failed'
    exit
fi

# cleanup the test data
 $sysbench_dir/sysbench/sysbench \
  --db-driver=mysql \
  --mysql-table-engine=innodb \
  --oltp-table-size=$oltp_table_size \
  --oltp-tables-count=$oltp_tables_count \
  --num-threads=$num_threads \
  --mysql-host=$mysql_host \
  --mysql-user=$mysql_user \
  --mysql-password=$mysql_password \
  --max-requests=$max_requests\
  --test=$test_name \
  cleanup

if [ $? -ne 0 ]; then
    echo 'cleanup the test data failed'
    exit
fi
