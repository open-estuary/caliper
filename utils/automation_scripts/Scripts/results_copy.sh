#!/bin/bash
db_path=/home/prashanth/DataBase_Jenkins_R7
dest_path=$HOME/caliper_output/frontend/frontend/data_files/Input_Logs/$6/
scp $1@$2:$db_path/$3/$4/results/yaml/$5 $dest_path
