#!/bin/bash

#####################
#args set mysql
mysql_user=${1:-root}
mysql_password=${2:-root}
mysql_table_engine=${3:-innodb}
mysql_host=${7:-localhost}
mysql_port=${8:-33306}
db_name=${9:-sbtest}

#####################
#args set oltp
oltp_table_size=${4:-100000}
oltp_tables_count=${5:-8}

#num_threads=$6
#max_requests=$10

#####################
#args modify
cpu_num=$(grep 'processor' /proc/cpuinfo |sort |uniq |wc -l)
let num_threads=cpu_num*2

max_requests=100000

#print args info
printf "%s[%3d]%5s: num_threads[${num_threads}] max_requests[${max_requests}]\n" "${FUNCNAME[0]}" ${LINENO} "Info"

#####################
#mysqld server check
ps -e |grep "mysqld" |awk -F'[ \t]+' '{print $NF}' |grep -q "^mysqld$"
if [ $? -ne 0 ]; then
    printf "%s[%3d]%5s: mysqld not run\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

#mysql env ready
sMysqlInfo=$(whereis mysql |cut -d: -f2-)
if [ -z "${sMysqlInfo}" ]; then
    printf "%s[%3d]%5s: mysql not found\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

#mysql lib
s1=$(find ${sMysqlInfo} -name "libmysqlclient.so" 2>/dev/null)
if [ -n "${s1}" ]; then
    s2=$(sed -n "1p" <<< "${s1}")
    drLibMysql=$(dirname "${s2}")
fi
if [ ! -d "${drLibMysql}" ]; then
    printf "%s[%3d]%5s: mysql lib not found\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi
dr1=$(sed "s/\./\\\./g" <<< "${drLibMysql}")
grep -q "\(^\|:\)${dr1}\(:\|$\)" <<< "${LD_LIBRARY_PATH}"
if [ $? -ne 0 ]; then
    export LD_LIBRARY_PATH=${drLibMysql}:${LD_LIBRARY_PATH}
fi
#printf "%s[%3d]%5s: LD_LIBRARY_PATH[${LD_LIBRARY_PATH}]\n" "${FUNCNAME[0]}" ${LINENO} "Info"

#mysql include
s1=$(find ${sMysqlInfo} -name "mysql.h" 2>/dev/null)
if [ -n "${s1}" ]; then
    s2=$(sed -n "1p" <<< "${s1}")
    drIncMysql=$(dirname "${s2}")
fi
if [ ! -d "${drIncMysql}" ]; then
    printf "%s[%3d]%5s: mysql include not found\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

#mysql client
s1=$(find ${sMysqlInfo} -name "mysql" 2>/dev/null |grep "/bin/mysql\$")
if [ -n "${s1}" ]; then
    s2=$(sed -n "1p" <<< "${s1}")
    drMysqlClient=$(dirname "${s2}")
fi
if [ ! -d "${drMysqlClient}" ]; then
    printf "%s[%3d]%5s: mysql client not found\n" "${FUNCNAME[0]}" ${LINENO} "Error"
    exit 1
fi

printf "%s[%3d]%5s: drLibMysql[${drLibMysql}] drIncMysql[${drIncMysql}] drMysqlClient[${drMysqlClient}]\n" "${FUNCNAME[0]}" ${LINENO} "Info"

#####################
#sysbench down
sysbench_dir=sysbench-0.5
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

#sysbench compile
pushd $sysbench_dir
  prefix=/usr/local/sysbench
  ./autogen.sh
  ./configure --prefix=$prefix --with-mysql-includes=$drIncMysql --with-mysql-libs=$drLibMysql
  make -s 
  make install
popd

#####################
#msql test data ready
dr1=$(sed "s/\./\\\./g" <<< "${drMysqlClient}")
grep -q "\(^\|:\)${dr1}\(:\|$\)" <<< "${PATH}"
if [ $? -ne 0 ]; then
    export PATH=${drMysqlClient}:${PATH}
fi

/usr/bin/expect > /dev/null 2>&1 <<EOF
    set timeout 40
    spawn mysql -u$mysql_user -p
    expect "*password:"
    send "$mysql_password\r"
    expect "mysql>"
    send "show databases;\r"
    expect {
        "$db_name" {
            send "drop database $db_name;\r"
            expect "mysql>"
            send "create database $db_name;\r"
            expect "mysql>"
        }
        "mysql>" {
            send "create database $db_name;\r"
        }
    }
    expect "mysql>"
    send "quit;\r"
    expect eof
EOF

#####################
#mysql env for sysbench
sR1=$(netstat -lnp |grep "[ \t]\+[0-9]\+/mysqld\([ \t]\+\|\$\)" |grep "[ \t]\+[^ \t0-9]\+[ \t]*\$")
sockMS=$(sed "s#^.*[ \t]\+\([^ \t0-9]\+\)[ \t]*\$#\1#" <<< "${sR1}")
sockSy="/var/lib/mysql/mysql.sock"
if [ "${sockMS}" != "${sockSy}" ]; then
    if [ ! -L "${sockSy}" ]; then
        drSockSy=$(dirname "${sockSy}")
        mkdir -p "${drSockSy}"
        ln -s "${sockMS}" "${sockSy}"
    fi
fi

#####################
#sysbench prepare the test data
test_name="$PWD/sysbench-0.5/sysbench/tests/db/oltp.lua"
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

#####################
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

#####################
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

#####################
