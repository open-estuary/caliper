#!/usr/bin/env python

import math


def geometric_mean(values):
    try:
        values = [float(value) for value in values
                if (value != 0 and value is not None)]
    except ValueError:
        return None

    n = len(values)
    if n == 0:
        return 0
    return math.exp(sum([math.log(x) for x in values]) / n)


class Scores_method:
    score = 0

    def __init__(score):
        score = score

    @staticmethod
    def exp_score_compute(score, base, index):
        # the algorithm is (x/n)**index, n equals to 10**base
        exp_score = math.pow(
                            score / (math.pow(10, base)),
                            index)
        return exp_score

    @staticmethod
    def compute_speed_score(score, base):
        # the algorithm is score/10**(base)
        tmp_score = score / math.pow(10, base)
        return tmp_score
