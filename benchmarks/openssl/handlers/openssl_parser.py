import re
import string
import math
import yaml

labels = ["^md5", "^sha1", "^des cbc", "^des ede3", "^sha256", "^sha512",
            "^aes-128 ige", "^aes-192 ige", "^aes-256 ige", "^rsa 2048",
            "^dsa 2048"]
keys = ["md5_speed", "sha1_speed", "des_speed", "3des_speed", "sha256_speed",
        "sha512_speed", "aes128_speed", "aes192_speed", "aes256_speed",
        "rsa_2048_sign", "rsa_2048_verify", "dsa_2048_sign",
        "dsa_2048_verify"]


def generate_value(content, outfp):
    keylist = {}
    for line in content.splitlines():
        for i in range(0, len(labels)):
            if re.search(labels[i], line):
                label = labels[i]
                field = line.split()
                if (label == labels[-1]):
                    keylist[keys[-2]] = field[-2]
                    keylist[keys[-1]] = field[-1]
                    outfp.write(keys[-2] + ": "+keylist[keys[-2]]+'\n')
                    outfp.write(keys[-1] + ": "+keylist[keys[-1]]+'\n')
                elif (label == labels[-2]):
                    keylist[keys[-4]] = field[-2]
                    keylist[keys[-3]] = field[-1]
                    outfp.write(keys[-4] + ": "+keylist[keys[-4]]+'\n')
                    outfp.write(keys[-3] + ": "+keylist[keys[-3]]+'\n')
                else:
                    keylist[keys[i]] = field[-2].split("k")[0]
                    outfp.write(keys[i] + ": "+keylist[keys[i]]+'\n')
    print keylist
    return keylist


def parser1(content, outfp):
    # need to standardization
    for line in content.splitlines():
        if re.search("^OpenSSL", line):
            outfp.write(line+'\n')
        elif re.search("^options", line):
            outfp.write(line+'\n')
        elif re.search("^compiler", line):
            outfp.write(line+'\n')
        else:
            pass
    key_list = generate_value(content, outfp)
    value_list = key_list.values()
    values = []
    for i in range(0, len(key_list)):
        try:
            values.append(string.atof(value_list[i]))
        except ValueError:
            continue
    try:
        value_float = [float(value) for value in values if value != 0]
    except ValueError:
        return None
    n = len(value_float)
    if n == 0:
        result = 1
    result = math.exp(sum([math.log(x) for x in values]) / n)
    # result = geometric_mean(values)
    return result

sym_labels = ["^rc4", "^des cbc", "^des ede3", '^idea cbc', '^seed cbc',
                '^rc2 cbc', '^blowfish cbc', '^cast cbc', '^aes-128 cbc',
                '^aes-192 cbc', '^aes-256 cbc', '^aes-128 ige',
                '^aes-192 ige', '^aes-256 ige']
hash_labels = ["^md5", "^sha1", "^sha256", "^sha512"]
dig_labels = ["^rsa", "^dsa", 'ecdsa']

dic = {}
dic['symmetric cyphers'] = {}
# dic['asymmetric cyphers'] = {}
dic['hash algorithm'] = {}
dic['digital sign'] = {}
dic['digital verify'] = {}
dic['digital sign']['rsa'] = []
dic['digital verify']['rsa'] = []
dic['digital sign']['dsa'] = []
dic['digital verify']['dsa'] = []
dic['digital sign']['ecdsa'] = []
dic['digital verify']['ecdsa'] = []


def get_openssl_dic(content, outfp):
    for line in content.splitlines():
        if re.search("^OpenSSL", line):
            outfp.write(line+'\n')
        elif re.search("^options", line):
            outfp.write(line+'\n')
        elif re.search("^compiler", line):
            outfp.write(line+'\n')
        else:
            get_list(line, outfp, 'symmetric cyphers', sym_labels)
            get_list(line, outfp, 'hash algorithm', hash_labels)

            for label in dig_labels:
                if re.search(label, line):
                    if label == 'ecdsa':
                        if re.findall("ecdsa\'s", line):
                            continue
                    list_label = re.findall('(\d+\.\d+)', line)
                    dic['digital sign'][label.split("^")[-1]]\
                            .append(list_label[-2])
                    dic['digital verify'][label.split("^")[-1]]\
                            .append(list_label[-1])
                    break
    outfp.write(yaml.dump(dic, default_flow_style=False))
    return dic


def get_list(line, outfp, flag, list_tables):
    for label in list_tables:
        if re.search(label, line):
            list_label = re.findall('(\d+\.\d+)', line)
            dic[flag][label.split('^')[-1]] = [ (float)(value)/100.0 for value in list_label ]
            # outfp.write(flag+' ' + label + ' ' + str(list_label))
            break

if __name__ == "__main__":
    infile = "openssl_output.log"
    outfile = "openssl_parser.log"
    infp = open(infile, "r")
    outfp = open(outfile, "a+")
    content = infp.read()
    get_openssl_dic(content, outfp)
    # parser1(content, outfp)
    outfp.close()
    infp.close()
