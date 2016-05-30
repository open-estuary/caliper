#!/usr/bin/python
import ConfigParser
import os 
import sys

#----------------------------------------------------------------------
def modify(path, client_ip, server_ip):
    """
    Create, read, update, delete config
    """
    if not os.path.exists(path):
        path = "../caliper/config/client_config.cfg"

    config = ConfigParser.ConfigParser()
    config.read(path)

    # change a value in the config
    config.set("CLIENT", "ip", client_ip)
    config.set("CLIENT", "port", 22)
    config.set("CLIENT", "user", "root")
    config.set("CLIENT", "password", "None")
    config.set("SERVER", "ip", server_ip)
    config.set("SERVER", "port", 22)
 
    # write changes back to the config file
    with open(path, "wb") as config_file:
        config.write(config_file)
 
#----------------------------------------------------------------------
 
modify( sys.argv[1], sys.argv[2], sys.argv[3] )
