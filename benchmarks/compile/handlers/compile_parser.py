#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time_parser

def compile_parser(content, outfp):
    return time_parser.time_parser(content, outfp)
