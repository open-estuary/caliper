#!/bin/bash

FILES=$HOME/caliper_output/*
#echo $FILES
ini_get () {
    awk -v section="$2" -v variable="$3" '
        $0 == "[" section "]" { in_section = 1; next }
        in_section && $1 == variable {
            $1=""
            $2=""
            sub(/^[[:space:]]+/, "")
            print
            exit 
        }
        in_section && $1 == "" {
            # we are at a blank line without finding the var in the section
            print "not found" > "/dev/stderr"
            exit 1
        }
    ' "$1"
}

db_ip=$( ini_get automation.cfg DATABASE ip )
db_user=$( ini_get automation.cfg DATABASE user )
db_passwd=$( ini_get automation.cfg DATABASE password )
db_folder=$( ini_get automation.cfg DATABASE folder )

caliper_option=$( ini_get automation.cfg EXECUTION_OPTION caliper_option )

if [ `echo $caliper_option | awk -F ' ' {'print $1'} | grep -c "f"` -ne 0 ]
then
	source_folder="$HOME/caliper_output/`echo $caliper_option | awk -F ' ' {'print $2'}`"
else
	source_folder="$HOME/caliper_output/output_0"
	for f in $FILES
	do
		if [ `echo $f | grep -c "/output"` -ne 0 ]
		then
			num_source=`echo $source_folder | awk -F '/' {'print $6'} | awk -F '_' {'print $2'}`
			num_file=`echo $f | awk -F '/' {'print $6'} | awk -F '_' {'print $2'}`	
			if [ $num_file -gt $num_source ]
			then
				source_folder=$f
			fi
		fi
	done
fi  
echo "folder name is $source_folder"
/usr/bin/expect << EOD
	spawn scp -r $source_folder $db_user@$db_ip:$db_folder
	expect {
		"assword" { send "$db_passwd\r"; exp_continue }
		"100%" { send_user "Successfully copied to $db_user@$db_ip:$db_folder\n" }
    		"Are you sure you want to continue connecting" { send "yes\r"; exp_continue}
	}
EOD
