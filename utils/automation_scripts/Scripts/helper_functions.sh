#!/bin/bash
release=`lsb_release -a | grep Release | awk -F ':' '{ print $2 }'`
delimiter_version="16.04"

autoSSH()
{
	user=$1
	ip=$2
	passwd=$3
	
	if [ ! -f "$HOME/.ssh/id_rsa.pub"  ]
	then
/usr/bin/expect << EOD
	spawn ssh-keygen
	expect {
		":" { send "\r"; exp_continue }
		eof 
	}
EOD
	fi
	
/usr/bin/expect << EOD
	spawn ssh-copy-id -i "$HOME/.ssh/id_rsa.pub" $user@$ip
	expect {
		"Are you sure you want to continue connecting" { send "yes\r"; exp_continue}
		"assword" { send "$passwd\r"; exp_continue }
	}
EOD

}
comment()
{
	#finding the pattern in server file
	fileName=$1
	line=`cat "$fileName" | grep -Fn "$3"`

	#checking if the pattern is in server file
	if [ -z $line ]
	then
		#finding the pattern in server file
		fileName=$2
		line=`cat "$client_def" | grep -Fn "$3"`
	fi
	
	#extracting the line num and the pattern of the test
	num=`echo "$line" | awk -F : '{ print $1 }'`
	string=`echo "$line" | awk -F : '{ print $2 }'`
	num2=$(($num+3))

	if [ ${string:0:1} != '#' -a ${string} != '\n' ] 
	then
		sed -i "$num,$num2 s/^/#/g" $fileName
	fi
}

uncomment()
{
	#finding the pattern in server file
	fileName=$1
	line=`cat $fileName | grep -Fn "$3"`

	#checking if the pattern is in server file
	if [ -z $line ]
	then
		#finding the pattern in server file
		fileName=$2
		line=`cat "$client_def" | grep -Fn "$3"`
	fi
	
	#extracting the line num and the pattern of the test
	num=`echo $line | awk -F : '{ print $1 }'`
	string=`echo "$line" | awk -F : '{ print $2 }'`
	num2=$(($num+3))

    if [ ${string:0:1} == '#' -a ${string} != '\n' ]
	then
		sed -i "$num,$num2 s/#//g" $fileName
	fi
}


checkCrossCompilation() 
{	
	target_arch=$1
	option=$2
	echo "option = $option"
	if [ $target_arch == 'aarch64' ]
	then 
		if [ ! -d "./toolchain/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux" ]
		then
			if [ -d toolchain ]
			then
				mkdir toolchain
			fi
			if [ -f "gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2" ]
			then
				tar -xvf gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 &
				wait
				mv gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux ./toolchain
			else
				echo "The toolchain is not present "
				echo "Do you want me to download it for you [y/n]"
				if [ "$option" == 'y' ]
				then
					choice="y"
				else
					read choice
				fi
				if [ $choice == 'y' ]
				then
					wget https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 &
					wait
					tar -xvf gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux.tar.bz2 
					wait
					mv gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux ./toolchain
				else
					echo "Please download toolchain and then try again"
					exit 1
				fi
			fi
		fi
		files_toolchain="toolchain/gcc-linaro-aarch64-linux-gnu-4.9-2014.09_linux/bin"
	elif [ $target_arch == 'arm_32' ]
	then
		if [ ! -d "./toolchain/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux" ]
		then 
			if [ -d "toolchain" ]
			then
				mkdir toolchain
			fi
			if [ -f "gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2" ]
			then
				tar -xvf gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
				wait
				mv gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux ./toolchain
			else
			    echo "The toolchain is not present "
				echo "Do you want me to download it for you [y/n]"
				if [ $option == "y" ]
				then
					choice="y"
				else
					read choice
				fi
				if [ $choice == 'y' ]
				then
					wget https://releases.linaro.org/14.09/components/toolchain/binaries/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
					wait
					tar -xvf gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux.tar.bz2 &
					wait
					mv gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux ./toolchain
				else
					echo "Please download toolchain and then try again"
					exit 1
				fi
			fi
		fi
		files_toolchain="toolchain/gcc-linaro-arm-linux-gnueabihf-4.9-2014.09_linux/bin"
	fi
   	export PATH=$PWD/$files_toolchain:$PATH
	if [ $? -ne 0 ]
	then 
		echo "Exporting the tool chain failed"
		return 1
	fi
	return 0
}

if [ `echo "$release <= $delimiter_version" | bc ` -eq 1 ] 
then
    ini_get () {
    	awk -v section="$2" -v variable="$3" '
        	$0 == "[" section "]" { in_section = 1; next }
        	in_section && $1 == variable {
            		$1=""
            		$2=""
            		gsub(/^[[:space:]]*/, "")
            		print
            		exit 
        	}
        	in_section && $1 == "" {
            		# we are at a blank line without finding the var in the section
            		print "Encounted a blank field in automation.cfg" > "/dev/stderr"
            		exit 1
        	}
    	' "$1"
	}
else
    ini_get () {
    	awk -v section="$2" -v variable="$3" '
        	$0 == "[" section "]" { in_section = 1; next }
        	in_section && $1 == variable {
            		$1=""
            		$2=""
            		gsub(/^[[ ]]*/, "")
            		print
            		exit 
        	}
        	in_section && $1 == "" {
            		# we are at a blank line without finding the var in the section
            		print "Encounted a blank field in automation.cfg" > "/dev/stderr"
            		exit 1
        	}
    	' "$1"
	}
fi
