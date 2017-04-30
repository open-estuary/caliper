import re
import string
import pdb


def openblas_parser(content, outfp):
    score = -1
    efficiency = -1
    dic = {}

    dic['openblas_value'] = {}
    dic['openblas_value']['TEST_01_200x200'] = {}
    dic['openblas_value']['TEST_02_400x400'] = {}
    dic['openblas_value']['TEST_03_1000x1000'] = {}
    dic['openblas_value']['TEST_04_2000x2000'] = {}
    dic['openblas_value']['TEST_05_3000x3000'] = {}
    dic['openblas_value']['TEST_06_4000x4000'] = {}

    dic['openblas_efficiency'] = {}
    dic['openblas_efficiency']['TEST_01_200x200'] = {}
    dic['openblas_efficiency']['TEST_02_400x400'] = {}
    dic['openblas_efficiency']['TEST_03_1000x1000'] = {}
    dic['openblas_efficiency']['TEST_04_2000x2000'] = {}
    dic['openblas_efficiency']['TEST_05_3000x3000'] = {}
    dic['openblas_efficiency']['TEST_06_4000x4000'] = {}

    for speed in re.findall("200x200\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 19200) * 100
        outfp.write("200x200 value is %s \n" % score)
        dic['openblas_value']['TEST_01_200x200'] = score
        dic['openblas_efficiency']['TEST_01_200x200'] = efficiency
        outfp.write("200x200 efficiency is %s \n" % efficiency)

    for speed in re.findall("400x400\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 19200) * 100
        outfp.write("400x400 value is %s \n" % score)
        dic['openblas_value']['TEST_02_400x400']= score
        dic['openblas_efficiency']['TEST_02_400x400']= efficiency
        outfp.write("400x400 efficiency is %s \n" % efficiency)

    for speed in re.findall("1000x1000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 19200) * 100
        outfp.write("1000x1000 value is %s \n" % score)
        dic['openblas_value']['TEST_03_1000x1000'] = score
        dic['openblas_efficiency']['TEST_03_1000x1000'] = efficiency
        outfp.write("1000x1000 efficiency is %s \n" % efficiency)

    for speed in re.findall("2000x2000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 19200) * 100
        outfp.write("2000x2000 value is %s \n" % score)
        dic['openblas_value']['TEST_04_2000x2000'] = score
        dic['openblas_efficiency']['TEST_04_2000x2000']= efficiency
        outfp.write("2000x2000 efficiency is %s \n" % efficiency)

    for speed in re.findall("3000x3000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 19200) * 100
        outfp.write("3000x3000 value is %s \n" % score)
        dic['openblas_value']['TEST_05_3000x3000'] = score
        dic['openblas_efficiency']['TEST_05_3000x3000'] = efficiency
        outfp.write("3000x3000 efficiency is %s \n" % efficiency)

    for speed in re.findall("4000x4000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 19200) * 100
        outfp.write("4000x4000 value is %s \n" % score)
        dic['openblas_value']['TEST_06_4000x4000'] = score
        dic['openblas_efficiency']['TEST_06_4000x4000'] = efficiency
        outfp.write("4000x4000 efficiency is %s \n" % efficiency)
            
    return dic


def openblas_parser_10(content, outfp):
    score = -1
    efficiency = -1
    dic = {}

    dic['openblas_value_10_cores'] = {}
    dic['openblas_value_10_cores']['TEST_01_200x200'] = {}
    dic['openblas_value_10_cores']['TEST_02_400x400'] = {}
    dic['openblas_value_10_cores']['TEST_03_1000x1000'] = {}
    dic['openblas_value_10_cores']['TEST_04_2000x2000'] = {}
    dic['openblas_value_10_cores']['TEST_05_3000x3000'] = {}
    dic['openblas_value_10_cores']['TEST_06_4000x4000'] = {}

    dic['openblas_efficiency_10_cores'] = {}
    dic['openblas_efficiency_10_cores']['TEST_01_200x200'] = {}
    dic['openblas_efficiency_10_cores']['TEST_02_400x400'] = {}
    dic['openblas_efficiency_10_cores']['TEST_03_1000x1000'] = {}
    dic['openblas_efficiency_10_cores']['TEST_04_2000x2000'] = {}
    dic['openblas_efficiency_10_cores']['TEST_05_3000x3000'] = {}
    dic['openblas_efficiency_10_cores']['TEST_06_4000x4000'] = {}

    for speed in re.findall("200x200\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 192000) * 100
        outfp.write("200x200 value is %s \n" % score)
        dic['openblas_value_10_cores']['TEST_01_200x200'] = score
        dic['openblas_efficiency_10_cores']['TEST_01_200x200'] = efficiency
        outfp.write("200x200 efficiency is %s \n" % efficiency)

    for speed in re.findall("400x400\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 192000) * 100
        outfp.write("400x400 value is %s \n" % score)
        dic['openblas_value_10_cores']['TEST_02_400x400']= score
        dic['openblas_efficiency_10_cores']['TEST_02_400x400']= efficiency
        outfp.write("400x400 efficiency is %s \n" % efficiency)

    for speed in re.findall("1000x1000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 192000) * 100
        outfp.write("1000x1000 value is %s \n" % score)
        dic['openblas_value_10_cores']['TEST_03_1000x1000'] = score
        dic['openblas_efficiency_10_cores']['TEST_03_1000x1000'] = efficiency
        outfp.write("1000x1000 efficiency is %s \n" % efficiency)

    for speed in re.findall("2000x2000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 192000) * 100
        outfp.write("2000x2000 value is %s \n" % score)
        dic['openblas_value_10_cores']['TEST_04_2000x2000'] = score
        dic['openblas_efficiency_10_cores']['TEST_04_2000x2000']= efficiency
        outfp.write("2000x2000 efficiency is %s \n" % efficiency)

    for speed in re.findall("3000x3000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 192000) * 100
        outfp.write("3000x3000 value is %s \n" % score)
        dic['openblas_value_10_cores']['TEST_05_3000x3000'] = score
        dic['openblas_efficiency_10_cores']['TEST_05_3000x3000'] = efficiency
        outfp.write("3000x3000 efficiency is %s \n" % efficiency)

    for speed in re.findall("4000x4000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 192000) * 100
        outfp.write("4000x4000 value is %s \n" % score)
        dic['openblas_value_10_cores']['TEST_06_4000x4000'] = score
        dic['openblas_efficiency_10_cores']['TEST_06_4000x4000'] = efficiency
        outfp.write("4000x4000 efficiency is %s \n" % efficiency)
            
    return dic

def openblas_parser_32(content, outfp):
    score = -1
    efficiency = -1
    dic = {}

    dic['openblas_value_32_cores'] = {}
    dic['openblas_value_32_cores']['TEST_01_200x200'] = {}
    dic['openblas_value_32_cores']['TEST_02_400x400'] = {}
    dic['openblas_value_32_cores']['TEST_03_1000x1000'] = {}
    dic['openblas_value_32_cores']['TEST_04_2000x2000'] = {}
    dic['openblas_value_32_cores']['TEST_05_3000x3000'] = {}
    dic['openblas_value_32_cores']['TEST_06_4000x4000'] = {}

    dic['openblas_efficiency_32_cores'] = {}
    dic['openblas_efficiency_32_cores']['TEST_01_200x200'] = {}
    dic['openblas_efficiency_32_cores']['TEST_02_400x400'] = {}
    dic['openblas_efficiency_32_cores']['TEST_03_1000x1000'] = {}
    dic['openblas_efficiency_32_cores']['TEST_04_2000x2000'] = {}
    dic['openblas_efficiency_32_cores']['TEST_05_3000x3000'] = {}
    dic['openblas_efficiency_32_cores']['TEST_06_4000x4000'] = {}

    for speed in re.findall("200x200\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 614400) * 100
        outfp.write("200x200 value is %s \n" % score)
        dic['openblas_value_32_cores']['TEST_01_200x200'] = score
        dic['openblas_efficiency_32_cores']['TEST_01_200x200'] = efficiency
        outfp.write("200x200 efficiency is %s \n" % efficiency)

    for speed in re.findall("400x400\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 614400) * 100
        outfp.write("400x400 value is %s \n" % score)
        dic['openblas_value_32_cores']['TEST_02_400x400']= score
        dic['openblas_efficiency_32_cores']['TEST_02_400x400']= efficiency
        outfp.write("400x400 efficiency is %s \n" % efficiency)

    for speed in re.findall("1000x1000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 614400) * 100
        outfp.write("1000x1000 value is %s \n" % score)
        dic['openblas_value_32_cores']['TEST_03_1000x1000'] = score
        dic['openblas_efficiency_32_cores']['TEST_03_1000x1000'] = efficiency
        outfp.write("1000x1000 efficiency is %s \n" % efficiency)

    for speed in re.findall("2000x2000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 614400) * 100
        outfp.write("2000x2000 value is %s \n" % score)
        dic['openblas_value_32_cores']['TEST_04_2000x2000'] = score
        dic['openblas_efficiency_32_cores']['TEST_04_2000x2000']= efficiency
        outfp.write("2000x2000 efficiency is %s \n" % efficiency)

    for speed in re.findall("3000x3000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 614400) * 100
        outfp.write("3000x3000 value is %s \n" % score)
        dic['openblas_value_32_cores']['TEST_05_3000x3000'] = score
        dic['openblas_efficiency_32_cores']['TEST_05_3000x3000'] = efficiency
        outfp.write("3000x3000 efficiency is %s \n" % efficiency)

    for speed in re.findall("4000x4000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 614400) * 100
        outfp.write("4000x4000 value is %s \n" % score)
        dic['openblas_value_32_cores']['TEST_06_4000x4000'] = score
        dic['openblas_efficiency_32_cores']['TEST_06_4000x4000'] = efficiency
        outfp.write("4000x4000 efficiency is %s \n" % efficiency)
            
    return dic


def openblas_parser_64(content, outfp):
    score = -1
    efficiency = -1
    dic = {}

    dic['openblas_value_64_cores'] = {}
    dic['openblas_value_64_cores']['TEST_01_200x200'] = {}
    dic['openblas_value_64_cores']['TEST_02_400x400'] = {}
    dic['openblas_value_64_cores']['TEST_03_1000x1000'] = {}
    dic['openblas_value_64_cores']['TEST_04_2000x2000'] = {}
    dic['openblas_value_64_cores']['TEST_05_3000x3000'] = {}
    dic['openblas_value_64_cores']['TEST_06_4000x4000'] = {}

    dic['openblas_efficiency_64_cores'] = {}
    dic['openblas_efficiency_64_cores']['TEST_01_200x200'] = {}
    dic['openblas_efficiency_64_cores']['TEST_02_400x400'] = {}
    dic['openblas_efficiency_64_cores']['TEST_03_1000x1000'] = {}
    dic['openblas_efficiency_64_cores']['TEST_04_2000x2000'] = {}
    dic['openblas_efficiency_64_cores']['TEST_05_3000x3000'] = {}
    dic['openblas_efficiency_64_cores']['TEST_06_4000x4000'] = {}

    for speed in re.findall("200x200\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 1228800) * 100
        outfp.write("200x200 value is %s \n" % score)
        dic['openblas_value_64_cores']['TEST_01_200x200'] = score
        dic['openblas_efficiency_64_cores']['TEST_01_200x200'] = efficiency
        outfp.write("200x200 efficiency is %s \n" % efficiency)

    for speed in re.findall("400x400\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 1228800) * 100
        outfp.write("400x400 value is %s \n" % score)
        dic['openblas_value_64_cores']['TEST_02_400x400']= score
        dic['openblas_efficiency_64_cores']['TEST_02_400x400']= efficiency
        outfp.write("400x400 efficiency is %s \n" % efficiency)

    for speed in re.findall("1000x1000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 1228800) * 100
        outfp.write("1000x1000 value is %s \n" % score)
        dic['openblas_value_64_cores']['TEST_03_1000x1000'] = score
        dic['openblas_efficiency_64_cores']['TEST_03_1000x1000'] = efficiency
        outfp.write("1000x1000 efficiency is %s \n" % efficiency)

    for speed in re.findall("2000x2000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 1228800) * 100
        outfp.write("2000x2000 value is %s \n" % score)
        dic['openblas_value_64_cores']['TEST_04_2000x2000'] = score
        dic['openblas_efficiency_64_cores']['TEST_04_2000x2000']= efficiency
        outfp.write("2000x2000 efficiency is %s \n" % efficiency)

    for speed in re.findall("3000x3000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 1228800) * 100
        outfp.write("3000x3000 value is %s \n" % score)
        dic['openblas_value_64_cores']['TEST_05_3000x3000'] = score
        dic['openblas_efficiency_64_cores']['TEST_05_3000x3000'] = efficiency
        outfp.write("3000x3000 efficiency is %s \n" % efficiency)

    for speed in re.findall("4000x4000\s+:\s+(.*?)MFlops.*?sec", content):
        score = string.atof(speed.strip())
        efficiency = (score / 1228800) * 100
        outfp.write("4000x4000 value is %s \n" % score)
        dic['openblas_value_64_cores']['TEST_06_4000x4000'] = score
        dic['openblas_efficiency_64_cores']['TEST_06_4000x4000'] = efficiency
        outfp.write("4000x4000 efficiency is %s \n" % efficiency)
            
    return dic
