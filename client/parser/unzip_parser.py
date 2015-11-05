#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    E-mail    :    wu.wu@hisilicon.com
#    Data      :    2015-08-17 16:33:07
#    Desc      :

import time_parser


def unzip_parser(content, outfp):
    return time_parser.time_parser(content, outfp)
