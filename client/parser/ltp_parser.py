import re
import sys


def ltpResult(content, outfp):
    sumPass = 0
    sumFail = 0
    sumConf = 0
    sumBrok = 0
    score = 0.0
    sumTotal = 0
    if len(re.findall("FAIL", content)):
       sumFail = sumFail + len(re.findall("FAIL", content))
    if len(re.findall("BROK", content)):
       sumBrok = sumBrok + len(re.findall("BROK", content))
    if len(re.findall("PASS", content)):
       sumPass = sumPass + len(re.findall("PASS", content))
    if len(re.findall("CONF", content)):
        sumConf = sumConf + len(re.findall("CONF", content))
 
    sumTotal = sumPass + sumFail + sumConf + sumBrok
    outfp.write('\nthe total number of testcases:  %d\n'
		    % (sumTotal))		

    outfp.write('the number of testcases passed are: %d\nthe number of failed testcases are: %d\n'
                  % (sumPass, sumFail))
    outfp.write('the number of testcases skipped are: %d\n \n'
		     % (sumBrok + sumConf))

    try:
        score = (0.0 + sumPass) / (sumTotal)
    except Exception:
        score = 0.0
    return score


def ltp_parser(content, outfp):
    score = -1
    score = ltpResult(content, outfp)
    return score


if __name__ == "__main__":
    fp = open(sys.argv[1], "r")
    text = fp.read()
    outfp = open("2.txt", "a+")
    ltp_parser(text, outfp)
    fp.close()
    outfp.close()
