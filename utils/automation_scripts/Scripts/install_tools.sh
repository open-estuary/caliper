#!/bin/bash
whoami=`whoami`
if [ $whoami == "root" ]
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
sudo su postgres <<EOF
psql -f caliperweb.sql
EOF
cd $caliper_output_path/NewCaliperweb
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8000
