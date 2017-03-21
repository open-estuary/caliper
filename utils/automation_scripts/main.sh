#!/bin/bash
# -*- coding:utf-8 -*-				
#################################################
#						#
#   Author  :   Dikshit N			#
#   E-mail  :   dikshit.n@huawei.com		#
#   Date    :   22/04/16			#
#################################################

automationFile="automation.cfg"
folder=".automationconfig"
path_config="./Scripts/client_automation_template.cfg"

source ./Scripts/helper_functions.sh

#checking if ".automationconfig folder is created or not"
if [[ ! -e $folder ]]
then
    	mkdir $folder
fi

client_count=`grep -o 'CLIENT_' "automation.cfg" | wc -l`
echo "Total Number of targets to be triggered are $client_count"
for (( clientid=1; clientid <= $client_count; clientid++ )); 
do 
	autoSetupSystem=$( ini_get $automationFile CLIENT_$clientid autoSetupSystem  )
	if [ -z "$autoSetupSystem" ]
	then
		autoSetupSystem="n"
	fi	

	checkDependency=$( ini_get $automationFile CLIENT_$clientid checkDependency  )
	if [ -z "$checkDependency" ]
	then
		checkDependency="y"
	fi
	Platform_name=$( ini_get $automationFile CLIENT_$clientid Platform_name )
	client_user=$( ini_get $automationFile CLIENT_$clientid user  )
	client_ip=$( ini_get $automationFile CLIENT_$clientid ip  )
	client_passwd=$( ini_get $automationFile CLIENT_$clientid password  )
	server_user=$( ini_get $automationFile TestNode user  )
	server_ip=$( ini_get $automationFile TestNode ip  )
	server_passwd=$( ini_get $automationFile TestNode password  )
	host_user=$( ini_get $automationFile HOST user  )
	host_ip=$( ini_get $automationFile HOST ip  )
	host_passwd=$( ini_get $automationFile HOST password )
	caliper_option=$( ini_get $automationFile CLIENT_$clientid caliper_option  )
	mount_point=$( ini_get $automationFile CLIENT_$clientid mount_point  )

	./Scripts/modify.py "$path_config" "$autoSetupSystem" "$checkDependency" "$Platform_name" "$client_user" "$client_ip" "$client_passwd" "$server_user" "$server_ip" "$server_passwd" "$host_user" "$host_ip" "$host_passwd" "$caliper_option" "$mount_point"
	if [ $? -ne 0 ]
	then
		echo "ERROR:FAILED TO MODIFY $path_config"
		exit 1
	fi

	`cp $path_config $folder/automation_$clientid.cfg`
	if [ $? -ne 0 ]
	then
		echo "FAILED TO COPY $path_config to $folder/automation_$clientid.cfg"
		exit 1
	fi

	target_arch=`ssh -t $client_user@$client_ip "hostname"`
	cd Scripts
	gnome-terminal -t "$target_arch" -e " bash -c '{ ./automation.sh $clientid; } 2>&1 | tee ../output_logs/$target_arch_$clientid'" 
	cd -
	
done

