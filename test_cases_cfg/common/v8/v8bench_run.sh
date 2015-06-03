run_v8bench() {
        echo "**    v8 javascript benchmark  test suite       **"        1>>result.txt  2>>error.txt
        cd browser/v8benchmark
        ../d8 run.js >../../v8.log
        cd ../../
        cat v8.log >> result.txt
        rm v8.log

        echo "**    v8 benchmark in browser  test suite       **"        1>>result.txt  2>>error.txt
        myBrowserPid=`/data/bin/ps ax | grep '[b]'rowser |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi
        logcat -c
        input keyevent 26
        input keyevent 82
        am start -a android.intent.action.VIEW -d file:///data/test/browser/v8benchmark/run.html -n com.android.browser/.BrowserActivity
        while :
        do
                myResult=`logcat -d | grep browser | grep "Score:"`
                myMatchStr="Score:"
                if [[ $myResult == *$myMatchStr* ]]
                then
                        logcat -d | grep browser | grep V8benchmark 1>>result.txt  2>>error.txt
                        break
                else
                        sleep 5
                        input keyevent 82
                fi
        done
   # let screen power off again
   input keyevent 26
        myBrowserPid=`/data/bin/ps ax | grep '[b]'rowser |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi

        echo "**    octane-bench javascript benchmark  test suite       **"        1>>result.txt  2>>error.txt
        cd browser/octane-bench
        ../d8 run.js >../../v8.log
        cd ../../
        cat v8.log >> result.txt
        rm v8.log

   # run octane-bench in browser
        echo "**    octane-bench in browser  test suite       **"        1>>result.txt  2>>error.txt
        myBrowserPid=`/data/bin/ps ax | grep '[b]'rowser |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi
        logcat -c
        input keyevent 26
        input keyevent 82
        am start -a android.intent.action.VIEW -d file:///data/test/browser/octane-bench/index.html?auto=1 -n com.android.browser/.BrowserActivity
        while :
        do
                myResult=`logcat -d | grep browser | grep "Octane Score"`
                myMatchStr="Octane Score"
                if [[ $myResult == *$myMatchStr* ]]
                then
                        logcat -d | grep browser | grep Octane 1>>result.txt  2>>error.txt
                        break
                else
                        sleep 5
                        input keyevent 82
                fi
        done
   # let screen power off again
   input keyevent 26
        myBrowserPid=`/data/bin/ps ax | grep '[b]'rowser |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi

        echo "**    sunspider javascript benchmark  test suite       **"                  1>>result.txt  2>>error.txt
        cd browser/sunspider-bench/tests/sunspider/
        ../../../d8 run.js >../../../../v8.log
        cd ../../../../
        cat v8.log                >>result.txt
        rm v8.log

        # run sunspider in browser
        echo "**    sunspider in browser  test suite       **"                           1>>result.txt  2>>error.txt
        myBrowserPid=`/data/bin/ps ax | grep '[b]'rowser |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi
        logcat -c
        input keyevent 26
        input keyevent 82
        am start -a android.intent.action.VIEW -d file:///data/test/browser/sunspider-bench/hosted/sunspider/driver.html -n com.android.browser/.BrowserActivity
        while :
        do
                myResult=`logcat -d | grep browser | grep "validate-input:"`
                myMatchStr="validate-input:"
                if [[ $myResult == *$myMatchStr* ]]
                then
                        logcat -d | grep browser             1>>result.txt  2>>error.txt
                        break
                else
                        sleep 5
                        input keyevent 82
                fi
        done
        # let screen power off again
        input keyevent 26
        myBrowserPid=`/data/bin/ps ax | grep '[b]'rowser |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi

        # run CanvasMark benchmark for browser
        # cd browser/CanvasMark
        # firefox index.html?auto=true
        # cd../../
   echo "**    CanvasMark benchmark  test suite       **"        1>>result.txt  2>>error.txt
   myBrowserPid=`/data/bin/ps ax | grep '[b]'rowser |cut -d \  -f1 | head -n 1`
   if [ -n "$myBrowserPid" ]; then
           kill $myBrowserPid
   fi
   logcat -c

   /* screen is already powered on, does not send power on/off key */
   input keyevent 26
   input keyevent 82
   am start -a android.intent.action.VIEW -d file:///data/test/browser/CanvasMark/index.html?auto=true -n com.android.browser/.BrowserActivity
   while :
   do
           myResult=`logcat -d | grep browser | grep "Test 7"`
           myMatchStr="Test 7"
           if [[ $myResult == *$myMatchStr* ]]
           then
                   logcat -d | grep browser | grep Test   1>>result.txt  2>>error.txt
          break
           else
                   sleep 5
                   input keyevent 82
           fi
   done
   # let screen power off again
   input keyevent 26
   myBrowserPid=`/data/bin/ps ax | grep browser |cut -d \  -f1 | head -n 1`
        if [ -n "$myBrowserPid" ]; then
                kill $myBrowserPid
        fi


        # run webgl benchmark for browser
        # cd browser/webgl-bench
        # firefox cubes.html
        # cd ../../
   # chroium does not support Webgl, chrome can not browse local file
}



run_v8bench
