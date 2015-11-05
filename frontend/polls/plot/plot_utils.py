#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    E-mail    :    wu.wu@hisilicon.com
#    Data      :    2015-08-17 10:53:32
#    Desc      :

TOTAL_SCORE = 'Total_Scores'
RESULT = 'results'
POINT_SCORE = 'Point_Scores'

PERF_FLAG = 1
FUNC_FLAG = 0


def get_category(num):
    if num == 1:
        return 'Performance'
    else:
        return 'Functional'
