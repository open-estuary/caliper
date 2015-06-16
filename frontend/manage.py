#!/usr/bin/env python
import os
import sys

def run_server(argv=None):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(argv)

if __name__=="__main__":
    run_server(sys.argv)
