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
    config.set("SERVER", "ip", server_ip)
    config.set("CLIENT", "port", "22")
    config.set("SERVER", "port", "22")
    config.set("CLIENT", "user", "root")
    config.set("CLIENT", "password", "None")
    dic_mapping = {
         "192.168.40.9":"RH2288-E52690V3-U15.04",
         "192.168.40.8":"RH2285-E52420V2-U15.04",
         "192.168.40.26":"D03-EST2.2-U15.04",
         "192.168.40.33":"D02-EST2.2-U15.04",
         "192.168.40.49":"PC-I5650-U15.04",
         "192.168.40.7":"DELLR7-E5606-U15.04"
         }
    if client_ip in dic_mapping.keys():
        if bool(config.get("CLIENT","name")):
            if config.get("CLIENT","name") != dic_mapping[client_ip]:
                 config.set("CLIENT", "name", "")
    if not bool(config.get("CLIENT","name")):
        if client_ip in dic_mapping.keys():
            config.set("CLIENT", "name", dic_mapping[client_ip])
    # write changes back to the config file
    with open(path, "wb") as config_file:
        config.write(config_file)
 
#----------------------------------------------------------------------
 
modify( sys.argv[1], sys.argv[2], sys.argv[3] )
