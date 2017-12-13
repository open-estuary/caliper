#/bin/sh
## How to build caliper.install:
# tar cvzf caliper-[ver].tar.gz caliper CaliperWeb
# cat caliper.install caliper-[ver].tar.gz > caliper-[ver].install

ARCHIVE=`awk '/^__ARCHIVE_BELOW__/ {print NR+1; exit 0}' "$0"`
#check user
user=`whoami`
if [ "$user" = 'root' ]; then
    echo "Please run this program as a normal user!"
    exit 0
fi

#init var
caliper_output_path="$HOME/caliper_output"
if [ ! -d "$caliper_output_path" ]; then
    mkdir -p $caliper_output_path
    chmod 777 $caliper_output_path
fi

#un-tar the caliper sourcecode tree
tail -n+$ARCHIVE "$0" | tar xzm -C $caliper_output_path

#mkdir $caliper_output_path/CaliperWeb/resources/upload/logs
if [ ! -d "$caliper_output_path/CaliperWeb/CaliperWeb/resources/upload" ]; then
    mkdir $caliper_output_path/CaliperWeb/CaliperWeb/resources/upload
    mkdir $caliper_output_path/CaliperWeb/CaliperWeb/resources/upload/logs
    chmod -R 777  $caliper_output_path/CaliperWeb/CaliperWeb/resources/upload
fi

#run installation script
sh $caliper_output_path/caliper/utils/automation_scripts/Scripts/install_tools.sh

#mv Caliperweb to /opt and run CaliperWeb script
sudo mv $caliper_output_path/CaliperWeb/ /opt/
sh /opt/CaliperWeb/script/CaliperWeb_install.sh

exit 0
#this line must be the last line!!!
__ARCHIVE_BELOW__
