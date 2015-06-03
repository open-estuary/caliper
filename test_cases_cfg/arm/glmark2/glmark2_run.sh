run_graphics() {

        echo "**    glmarks  test suite       **"        1>>result.txt  2>>error.txt
        myBrowserPid=`/data/bin/ps ax | grep '[g]'lmark2 |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi
        logcat -c

   /* screen is already powered on, does not send power on/off key again */
        input keyevent 26
        input keyevent 82
        am start -W org.linaro.glmark2/.Glmark2Activity
        while :
        do
                myResult=`logcat -d  | grep "glmark2 Score"`
                myMatchStr="glmark2 Score"
                if [[ $myResult == *$myMatchStr* ]]
                then
                        logcat -d  | grep "glmark2" | tail -n 45   1>>result.txt  2>>error.txt
                        break
                else
                        sleep 5
                        input keyevent 82
                fi
        done
        myBrowserPid=`/data/bin/ps ax | grep '[g]'lmark2 |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi
   # let screen power off again
   input keyevent 26
}

run_graphics
