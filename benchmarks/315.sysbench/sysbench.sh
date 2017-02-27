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

export PATH=$PATH:/usr/local/mysql/bin

if ! hash mysqld; then
    echo 'The mysql server has not been installed'
    exit 1
fi

if [ ! -d $sysbench_dir ]; then
    n1=0
    iRt1=1
    s1=
    while [ ${n1} -lt 5 ]; do
        s1=$(bzr branch lp:~sysbench-developers/sysbench/0.5 $sysbench_dir 2>&1)
        if [ $? -eq 0 ]; then
            iRt1=0
            break;
        fi
        let n1+=1
    done
    printf "%s[%3s]%5s: bzr [${PWD}] while [${n1}] times status[${iRt1}]\n" "${FUNCNAME[0]}" ${LINENO} "Info"
    echo "${s1}"
    if [ ${iRt1} -ne 0 ]; then
        echo 'Download the sysbench failed'
        exit 1
    fi
fi

mysql_loc=($(whereis mysql))

OSname_Ubuntu=`cat /etc/*release | grep -c "Ubuntu"`
OSname_CentOS=`cat /etc/*release | grep -c "CentOS"`
if [ ! $OSname_Ubuntu -eq 0 ]; then
    for i in ${mysql_loc[@]}; do
        tmp=$(echo $i | grep '/lib/mysql')
        if [ $? -eq 0 ]; then
            mysql_lib=$tmp
        else
            tmp1=$(echo $i | grep '/include/mysql')
            if [ $? -eq 0 ]; then
                mysql_include=$tmp1
            fi
        fi
    done
elif [ ! $OSname_CentOS -eq 0 ]; then
    for i in ${mysql_loc[@]}; do
        grep -q '/lib[0-9]*/mysql' <<< "${i}"
        if [ $? -eq 0 ]; then
             mysql_lib=${i}
        else
            grep -q '/include/mysql' <<< "${i}"
            if [ $? -eq 0 ]; then
                mysql_include=${i}
            fi
        fi
    done
else
    echo "selected OS in not Ubuntu or centos"
    exit 1
fi

if [ "$mysql_lib" == "" -o "$mysql_include" == "" ]; then
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

/usr/bin/expect <<EOF
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

if [ ! $OSname_CentOS -eq 0 ]; then
    sR1=$(netstat -lnp |grep "[ \t]\+[0-9]\+/mysqld\([ \t]\+\|\$\)" |grep "[ \t]\+[^ \t0-9]\+[ \t]*\$")
    sockMS=$(sed "s#^.*[ \t]\+\([^ \t0-9]\+\)[ \t]*\$#\1#" <<< "${sR1}")
    sockSysb="/var/lib/mysql/mysql.sock"
    if [ "${sockMS}" != "${sockSysb}" ]; then
        if [ ! -L "${sockSysb}" ]; then
            ln -s "${sockMS}" "${sockSysb}"
        fi
    fi
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
