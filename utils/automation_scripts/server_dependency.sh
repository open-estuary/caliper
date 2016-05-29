#!/bin/bash
dependency=('netperf' 'iperf')
flag=(1 1)
clear
echo "SERVER"
echo -e "\n\t\tServer Dependency"
for i in `seq 0 $((${#dependency[@]}-1)) `
do 
    check=`dpkg-query -W -f='${Status}' ${dependency[$i]} | grep -c "ok installed"`
    if [ $check -eq 1 ];then
        echo -e "\n ${dependency[$i]} is already installed  "
    else
        echo -e "\n ${dependency[$i]}  is not installed.do u want to install(y/n)"
        read choice
        if [ $choice == 'y' ];then
             sudo dpkg --configure -a
             sudo apt-get update &
             wait
             sudo apt-get build-dep ${dependency[$i]} -y &
             wait
             sudo apt-get install ${dependency[$i]} -y &
             wait
             if [ $? -ne 0 ];then
                echo -e "\n\t\tCould Not install please try again"
                flag[$i]=0
             fi
        else
            echo -e "\n ${dependency[$i]} is not installed.Please note that ${dependency[$i]} will not work in Caliper"
            ${flag[$i]}=0
        fi
   fi     
done



for i in `seq 0 $((${#flag[@]}-1)) ` 
do    
    j=${flag[$i]}
    if [ $j -eq 1 -a $i -eq 0 ];then
        if  ! ps -ef |grep "netperf" | grep -v grep ;then 
            echo -e "\n\t\tnetperf service not running"
            sudo service netperf restart
            wait
            echo "\n\t\tdone restarting netperf"
            if [ $? -ne 0 ];then
                echo -e "\n\t\tCould Not restart Netperf please try again"
                exit 1
            fi
        fi
    elif [ $j -eq 1 -a $i -eq 1 ];then
        if  ! ps -ef |grep "iperf" | grep -v grep  ;then 
            iperf -s&
            if [ $? -ne 0 ];then
                echo -e "\n\t\tCould Not restart Iperf please try again"
                exit 1
            fi
        fi
   fi         

done
