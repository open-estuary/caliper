#!/bin/bash

install_dependency="$HOME/caliper_output"
if [ ! -d $install_dependency ]
then
    sudo mkdir -p $install_dependency
fi
sudo chmod 777 $install_dependency
cd $install_dependency

caliper="caliper"
#if [ -d $caliper ]
#then
#    rm -rf $caliper
#fi
git clone https://github.com/TSestuary/caliper.git
git clone https://github.com/TSestuary/NewCaliperweb.git
cd $caliper
sudo python setup.py install
cd $install_dependency/caliper/utils/automation_scripts/Scripts
./install_dependency.sh
cd $install_dependency/NewCaliperweb
sudo su - postgres
python manage.py runserver 8000
