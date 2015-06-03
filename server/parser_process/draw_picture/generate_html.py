import os
import sys
import shutil
import stat
import pdb

from caliper.client.shared import caliper_path

LOCATION = os.path.dirname(sys.modules[__name__].__file__)
RESULTS_DIR = caliper_path.RESULTS_DIR
HTML_DIR = os.path.join(RESULTS_DIR, 'html')

def generate_html():
    pwd = os.getcwd()
    os.chdir(LOCATION)
    os.chmod("./html_md", stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO )
    os.chmod("./get_hardware_info", stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO )
    os.system("./html_md %s" % HTML_DIR)
    os.chdir(pwd)

if __name__=="__main__":
    generate_html()
