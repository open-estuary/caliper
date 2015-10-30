#!/usr/bin/expect

# prepare the sbtest database in mysql
set timeout 40

set mysql_user [lindex $argv 0]
set mysql_passwd [lindex $argv 1]
set db_name [lindex $argv 2]

spawn mysql -u$mysql_user -p
expect "*password:"
send "$mysql_passwd\r"
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
