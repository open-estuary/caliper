#!/bin/bash

#####################################################################################
config="config.json"
ubuntu_x86_packages=(`sed -n '/^\"ubuntu_x86_package\":\[/,/^\],/p' $config 2>/dev/null | sed 's/\"//g' | grep -Po "(?<=platform:)(.*?)(?=,)" | sort -u`)
ubuntu_arm_packages=(`sed -n '/^\"ubuntu_arm_packages\":\[/,/^\],/p' $config 2>/dev/null | sed 's/\"//g' | grep -Po "(?<=platform:)(.*?)(?=,)" | sort -u`)
centos_x86_packages=(`sed -n '/^\"centos_x86_packages\":\[/,/^\],/p' $config 2>/dev/null | sed 's/\"//g' | grep -Po "(?<=platform:)(.*?)(?=,)" | sort -u`)
centos_arm_packages=(`sed -n '/^\"centos_arm_packages\":\[/,/^\]/p' $config 2>/dev/null | sed 's/\"//g' | grep -Po "(?<=platform:)(.*?)(?=,)" | sort -u`)

#####################################################################################
install_dependency="$HOME/caliper_output"
if [ ! -d $install_dependency ]
then
    sudo mkdir -p $install_dependency
fi
sudo chmod 777 $install_dependency
cd $install_dependency

file_present="$install_dependency/install_dependency_output_summary.txt"
if [ -f $file_present ]
then
    sudo rm $file_present
fi
sudo touch $file_present
sudo chmod 777 $file_present
ERROR="ERROR-IN-AUTOMATION"
UPDATE=0
clear
architecture=`uname -i`
Osname_Ubuntu=`cat /etc/*release | grep -c "Ubuntu"`
if [ ! $Osname_Ubuntu -eq 0 ]
then
    if [ ! $architecture == "aarch64" ]
    then
        packages=`echo ${ubuntu_x86_packages[*]} | sed 's/ /, /g'`
        target_packages=`echo $packages | tr ',' ' '`
    else
        packages=`echo ${ubuntu_arm_packages[*]} | sed 's/ /, /g'`
        target_packages=`echo $packages | tr ',' ' '`
    fi
    for pack in $target_packages
    do
    #checking to see if all the target dependent packages are installed
        check=`dpkg-query -W -f='${Status}' $pack | grep -c "ok installed"`
        if [ $check -eq 0 ]
        then
            sudo dpkg --configure -a
            if [ $UPDATE=0 ]
            then
                UPDATE=1
                sudo apt-get update
            fi
            sudo apt-get build-dep $pack -y
            sudo apt-get install $pack -y
            if [ $? -ne 0 ]
            then
                echo -e "target $ERROR:$pack is not installed properly"
                echo -e "\n\t\t$ERROR:$pack is not installed properly" >> $file_present
                continue
            else
                echo "$pack is installed" >>  $file_present
                echo "Finished install $pack"
            fi
        else
           echo "$pack is installed" >>  $file_present
           echo "Finished install $pack"
        fi
    done
else
    if [ ! $architecture=="aarch64" ]
    then
        packages=`echo ${centos_x86_packages[*]} | sed 's/ /, /g'`
        target_packages=`echo $packages | tr ',' ' '`
    else
        packages=`echo ${centos_arm_packages[*]} | sed 's/ /, /g'`
        target_packages=`echo $packages | tr ',' ' '`
    fi

    for centospack in $target_packages
    do
        #checking to see if all the target dependent packages are installed
        check=`rpm -qa $pack`
        if [  -z "$check" ]
        then
            if [ $UPDATE=0 ]
            then
                UPDATE=1
                sudo yum update &
                wait
            fi
            sudo yum-builddep -y $centospack &
            wait
            sudo yum install -y $centospack &
            wait
            if [ $? -ne 0 ]
            then
                echo -e "target $ERROR:$centospack is not installed properly"
                echo -e "\n\t\t$ERROR:$centospack is not installed properly" >>  $file_present
                continue
            fi
        else
           echo "$centospack is installed" >> $file_present
        fi

    done
fi

# install python-pip
pip_packages=('Django' 'numpy' 'matplotlib' 'openpyxl' 'psycopg2' 'poster')

for i in `seq 0 $((${#pip_packages[@]}-1)) `
do
    #chcking to see if python packages are installed
    check=`pip show ${pip_packages[$i]} | grep -c "${pip_packages[$i]}"`
    if [ $check -eq 0 ]
    then
        # if force option is passed thn forcefully run the scripts

        if [ ${pip_packages[$i]} == "Django" ]
        then
            sudo pip install Django==1.11.4
        elif [ ${pip_packages[$i]} == "matplotlib" ]
        then
            sudo pip install matplotlib==1.3.1
        elif [ ${pip_packages[$i]} == "numpy" ]
        then
            sudo pip install numpy==1.8.2
        else
            sudo pip install ${pip_packages[$i]}
        fi
        if [ $? -ne 0 ]
        then
            echo -e "host $ERROR:${pip_packages[$i]} is not installed properly\n"
            echo -e "\n\t\t$ERROR:${pip_packages[$i]} is not installed properly" >> $file_present
            continue
        else
            echo "${pip_packages[$i]} is installed" >> $file_present
            echo "Finished install ${pip_packages[$i]}"
        fi
    else
        echo "${pip_packages[$i]} is installed" >> $file_present
        echo "Finished install ${pip_packages[$i]}"
    fi
done

check=`sudo find /usr/local/lib -name libpcre.so | grep -c libpcre.so`
if [ $check -ne 1 ];then
    wget http://www.estuarydev.org/caliper/pcre-8.39.tar.gz
    tar -zxvf pcre-8.39.tar.gz
    sudo chmod 777 pcre-8.39
    cd pcre-8.39
    ./configure
    make -j32
    sudo make install
    cd ..
    sudo rm -rf pcre-8.39
    sudo rm -rf pcre-8.39.tar.gz
fi
sudo chmod 775 $install_dependency