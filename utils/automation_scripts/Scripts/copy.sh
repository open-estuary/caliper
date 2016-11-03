#!/bin/bash
source helper_functions.sh
FILES=$HOME/caliper_output/*
COPY_CFG="$1"

if [ ! -f $COPY_CFG ]
then
	echo "$COPY_CFG does not exits, Please create it as per Automation_UserDoc"
	exit 1
fi

db_ip=$( ini_get $COPY_CFG DATABASE ip )
db_user=$( ini_get $COPY_CFG DATABASE user )
db_passwd=$( ini_get $COPY_CFG DATABASE password )
db_folder=$( ini_get $COPY_CFG DATABASE folder )

source_folder="$HOME/caliper_output/$2/output"
if [ ! -f $source_folder ]
then
	echo "$source_folder does not exits"
	exit 1
fi

/usr/bin/expect << EOD
	spawn scp -r $source_folder $db_user@$db_ip:$db_folder
	expect {
		"assword" { send "$db_passwd\r"; exp_continue }
		"100%" { send_user "Successfully copied to $db_user@$db_ip:$db_folder\n" }
    		"Are you sure you want to continue connecting" { send "yes\r"; exp_continue}
	}
EOD
