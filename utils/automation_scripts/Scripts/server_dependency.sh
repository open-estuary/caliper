#!/bin/bash

server_dependency="server_dependency_dir"

if [ ! -d $server_dependency ]
then
        sudo mkdir -p $server_dependency
fi
cd $server_dependency

file_present=server_dependency_output_summary.txt
if [ -f $file_present ]
then
    sudo rm server_dependency_output_summary.txt
fi

ERROR="ERROR-IN-AUTOMATION"
dependency=('netperf' 'iperf3')
UPDATE=0
flag=(1 1)
clear
echo "SERVER"
echo -e "\n\t\tServer Dependency"
for i in `seq 0 $((${#dependency[@]}-1)) `
do 
    check=`dpkg-query -W -f='${Status}' ${dependency[$i]} | grep -c "ok installed"`
    if [ $check -eq 1 ];then
        echo -e "\n ${dependency[$i]} is already installed" >> server_dependency_output_summary.txt
    else
	# if force option is passed thn forcefully run the scripts
        if [ $1 = "y" ]
        then
            choice="y"
        else
            echo "${host_packages[$i]} is not installed, would you like to install(y/n)" >> server_dependency_output_summary.txt
            read choice
        fi
        if [ $choice == 'y' ];then
            sudo dpkg --configure -a
            if [ $UPDATE=0 ]
            then
                UPDATE=1
                sudo apt-get update &
                wait
            fi
             sudo apt-get build-dep ${dependency[$i]} -y &
             wait
             sudo apt-get install ${dependency[$i]} -y &
             wait
             if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not install please try again" >> server_dependency_output_summary.txt
                flag[$i]=0
             fi
        else
            echo -e "\n ${dependency[$i]} is not installed.Please note that ${dependency[$i]} will not work in Caliper" >> server_dependency_output_summary.txt
            ${flag[$i]}=0
        fi
   fi     
done



for i in `seq 0 $((${#flag[@]}-1)) ` 
do    
    j=${flag[$i]}
    if [ $j -eq 1 -a $i -eq 0 ];then
        if  ! ps -ef | grep "netserver" | grep -v grep ;then 
            echo -e "\n\t\tnetperf service not running"
            sudo service netperf restart
            wait
            echo "\n\t\tdone restarting netperf"
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Netperf please try again" >> server_dependency_output_summary.txt
                exit 1
            fi
        fi
    elif [ $j -eq 1 -a $i -eq 1 ];then
        if  ! ps -ef |grep "iperf3" | grep -v grep  ;then 
            echo "78787"
            iperf3 -s &
            if [ $? -ne 0 ];then
                echo -e "\n\t\t$ERROR:Could Not restart Iperf please try again" >> server_dependency_output_summary.txt
                exit 1
            fi
        fi
   fi         

done
