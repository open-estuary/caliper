#!/bin/bash
Whoami=`whoami`
if [ "$Whoami" = "root" ]
then
    echo "Please run this program as normal user."
    exit 0
fi
caliper_output_path="$HOME/caliper_output"
if [ ! -d $caliper_output_path ]
then
    sudo mkdir -p $caliper_output_path
fi
sudo chmod 777 $caliper_output_path
cd $caliper_output_path

caliper="$caliper_output_path/caliper"
#if [ -d $caliper ]
#then
#    rm -rf $caliper
#fi
#git clone https://github.com/TSestuary/caliper.git
#git clone https://github.com/TSestuary/NewCaliperweb.git
cd $caliper
sudo python setup.py install
cd $caliper_output_path/caliper/utils/automation_scripts/Scripts
./install_dependency.sh

#generate ssh key and copy to ifself
if [ ! -f $HOME/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -P '' -f $HOME/.ssh/id_rsa
fi

cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys

sudo su<<EOF
    mkdir -p /root/.ssh
    cat /home/$Whoami/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
EOF

sudo su postgres <<EOF
psql -f caliperweb.sql
EOF
cd $caliper_output_path/NewCaliperweb
python manage.py makemigrations
python manage.py migrate
/usr/bin/expect <<EOF
spawn psql -U caliperuser -h 127.0.0.1 -d calipernewdb -f $caliper_output_path/NewCaliperweb/resources/caliper.psql
expect "caliperuser"
send "caliperts\r"
expect eof
EOF
python manage.py runserver 0.0.0.0:8000 &
