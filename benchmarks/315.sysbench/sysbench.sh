#!/bin/bash
sysbench_dir=sysbench-0.5
cpu_num=$(grep 'processor' /proc/cpuinfo |sort |uniq |wc -l)

db_driver=mysql
: ${mysql_user:=$1}
: ${mysql_user:=root}
: ${mysql_password:=$2}
: ${mysql_password:=123456}
: ${mysql_table_engine:=$3}
: ${mysql_table_engine:=innodb}
: ${oltp_table_size:=$4}
: ${oltp_table_size:=100000}
: ${oltp_tables_count:=$5}
: ${oltp_tables_count:=8}
#: ${num_threads:=$6}
: ${num_threads:=$((cpu_num*2))}
: ${mysql_host:=$7}
: ${mysql_host:=localhost}
: ${mysql_port:=$8}
: ${mysql_port:=33306}
: ${db_name:=$9}
: ${db_name:=sbtest}
#: ${max_requests:=$10}
: ${max_requests:=100000}
test_name="$PWD/sysbench-0.5/sysbench/tests/db/oltp.lua"
echo "max_requests are $max_requests"
sudo apt-get install libtool autoconf automake -y

#exists=$(ps -aux | grep 'mysqld')
mysql_version=$(mysql --version | awk '{ print $1"-" $2 ": " $3}')
exists=$(echo $mysql_version|awk -F":" '{print $1}')
if [ "$exists"x = "mysql-Ver"x ]; then
    echo "Found  $mysql_version  installed"
else
    echo "The mysql server has not been installed,Please install mysql,Refe caliper documentation"
    exit 1
fi

sudo apt-get install libmysqlclient-dev -y
sudo apt-get install libmysqld-dev -y

sudo apt-get install bzr -y

if [ ! -d $sysbench_dir ]; then
  bzr branch lp:~sysbench-developers/sysbench/0.5 $sysbench_dir
  if [ $? -ne 0 ]; then
    echo 'Download the sysbench failed'
    exit 1
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

if [ "$mysql_lib"x = ""x ] or [ "$mysql_include"x = ""x ]; then
    echo 'mysql has not been installed right'
    exit 1
fi

if [ ! -d $sysbench_dir ]; then
    echo 'sysbench has not been download completely'
    exit 1
fi

export PATH=$PATH:/usr/local

pushd $sysbench_dir
  prefix=/usr/local/sysbench
  ./autogen.sh
  ./configure --prefix=$prefix --with-mysql-includes=$mysql_include --with-mysql-libs=$mysql_lib
  make -s 
  make install
popd

sudo apt-get install expect -y
if [ $? -ne 0 ]; then 
    echo "install expect failed"
    exit 1
fi

/usr/bin/expect > /dev/null 2>&1 <<EOF
set timeout 40

spawn mysql -u$mysql_user -p
expect "*password:"
send "$mysql_password\r"
expect "mysql>"
send "show databases;\r"

expect {
 "$db_name"
 {
     send "drop database $db_name;\r"
     expect "mysql>"
     send "create database $db_name;\r"
     expect "mysql>"
 }
 "mysql>"
 {
     send "create database $db_name;\r"
 }
}
expect "mysql>"
send "quit;\r"
expect eof
EOF

if [ $max_requests -eq 0 ]; then 
    max_requests=100000
fi
set -x
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
    exit 1
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
    exit 1
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
    exit 1
fi
