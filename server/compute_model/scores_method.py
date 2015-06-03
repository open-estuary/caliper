## wuyanjun 00291783
## wu.wu@hisilicon.com
## copyright

import string
import math
import re

def geometric_mean(values):
    try:
        values = [ float(value) for value in values if (value != 0 and value != None) ]
    except ValueError:
        return None

    product = 1
    n = len(values)
    if n==0:
        return 0
    return math.exp(sum([math.log(x) for x in values]) / n)

class Scores_method:

    def __init__(score):
        self.score = score

    @staticmethod
    def exp_score_compute(score, base, index):
        # the algorithm is (x/n)**index, n equals to 10**base
        exp_score = math.pow(score/(math.pow(10, base)), index)
        return exp_score
   
    @staticmethod
    def compute_speed_score(score, base):
        # the algorithm is score/10**(base)
        tmp_score = score / math.pow(10, base)
        return tmp_score


