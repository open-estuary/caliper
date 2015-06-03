run_powerMgr() {
        echo "**      power management test suite       **"        1>>result.txt  2>>error.txt
        cd powerMgr
        ./pm-qa_android.sh          1>>result.txt  2>>error.txt
        cd ../
        cat powerMgr/result.txt   >> result.txt
        cat powerMgr/error.txt    >> error.txt
        rm -rf powerMgr/result.txt
        rm -rf powerMgr/error.txt
}

run_powerMgr
