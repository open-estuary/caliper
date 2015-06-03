# !/bin/sh

version=$( grep -R 'LMBENCH_VER' lmbench )
version=$( echo $version | awk -F ':' '{print $2}' | awk -F ']' '{print $1}')

sed -i "s/<version>/$version/g" lmbench_bandwidth
sed -i "s/<version>/$version/g" lmbench_latency

HOSTNAME=$(hostname)
cp CONFIG CONFIG.${HOSTNAME}

filename="results/${HOSTNAME}.0"

decision=$1
if [ "$decision"x == "latency"x ]; then
    ./lmbench_latency CONFIG.${HOSTNAME} 2>$filename
else
    if [ "$decision"x == "bandwidth"x ]; then
        ./lmbench_bandwidth CONFIG.${HOSTNAME} 2>$filename
    fi
fi

line_num=0
while read line
do
    value=$(echo $line | grep '^\[lmbench3\.0')
    if [ "$value"x != ""x ]
    then
        break
    fi
    let line_num=$line_num+1
    echo $line_num
done < $filename
#$filename

echo $line_num

if [ $line_num -ge 1 ]
then
    echo '1234'
    sed -i "1,${line_num}d" $filename
fi

cat $filename
#if_suc=$(cat $filename | grep '^\[lmbench3\.0')
#if [ "$if_suc"x != ""x ]
#then
#    make summary > result_see
#fi
#cat result_see
#
