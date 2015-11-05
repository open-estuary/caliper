import re
import sys


def ltpResult(content, outfp):
    sumPass = 0
    sumFail = 0
    sumInfo = 0
    sumBrok = 0
    score = 0.0

    if len(re.findall("TFAIL", content)):
        sumFail = sumFail + len(re.findall("TFAIL", content))
    if len(re.findall("TBROK", content)):
        sumBrok = sumBrok + len(re.findall("TBROK", content))
    if len(re.findall("TPASS", content)):
        sumPass = sumPass + len(re.findall("TPASS", content))
    # if len(re.findall("TINFO", content)):
    #    sumInfo = sumInfo + len(re.findall("TINFO", content))

    outfp.write('the total number of testcases is %d\n'
                    % (sumPass + sumFail + sumInfo + sumBrok))
    outfp.write('the tesecases passed are %d, failed are %d\n'
                    % (sumPass, sumFail))
    try:
        score = (0.0 + sumPass) / (sumPass + sumFail + sumInfo + sumBrok)\
                * 100
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
