echo `python check_status.py $HOME/caliper_output/$1_$2/output/results_summary.log`
value=`python check_status.py $HOME/caliper_output/$1_$2/output/results_summary.log | wc -l`
if [ $value -gt 0 ]; then
	echo "The tools have failed check the log"
else
	echo "print successful execution"
fi
