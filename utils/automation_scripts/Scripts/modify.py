#!/usr/bin/python
import ConfigParser
import os 
import sys

def insertChar(mystring, position, chartoinsert ):
    longi = len(mystring)
    mystring   =  mystring[:position] + chartoinsert + mystring[position:] 
    return mystring  

def modify_client(path, autocheck, dpe_option, Platform_name, client_user, client_ip, clientpwd, server_user, server_ip, serverpwd, host_user, host_ip, hostpwd, caliper_options, mount_point ):
    """
    Create, read, update, delete config
    """
    if not os.path.exists(path):
	print path + "Does not exits"
        sys.exit(1)
    
    try:
         config = ConfigParser.ConfigParser()
	 config.optionxform=str
         config.read(path)
         #serverpwd = insertChar(serverpwd,serverpwd.index('$'), '\\')
         if hostpwd.find("$") !=-1 :
     	     hostpwd = insertChar(hostpwd,hostpwd.index('$'), '\\')
         # change a value in the config
         config.set("CLIENT", "ip", client_ip)
         config.set("SERVER", "ip", server_ip)
         config.set("SERVER", "password", serverpwd)
         config.set("CLIENT", "password", clientpwd)
         config.set("SERVER", "user", server_user)
         config.set("CLIENT", "user", client_user)
         config.set("CLIENT", "caliper_option",caliper_options)
         config.set("CLIENT", "checkDependency", dpe_option)
         config.set("CLIENT", "autoSetupSystem", autocheck)
         config.set("CLIENT", "Platform_name", Platform_name)
         config.set("HOST", "ip", host_ip)
         config.set("HOST", "user", host_user)
         config.set("HOST", "password", hostpwd)
         config.set("CLIENT","mount_point",mount_point)
        
         # write changes back to the config file
         with open(path, "wb") as config_file:
             config.write(config_file)

    except Exception as e:
	 print "ERROR"
         print e
	 sys.exit(1)

#----------------------------------------------------------------------
def modify(path, client_ip, server_ip):
    """
    Create, read, update, delete config
    """
    if not os.path.exists(path):
        sys.exit(1)

    
    try:
         config = ConfigParser.ConfigParser()
	 config.optionxform=str
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
              "192.168.40.33":"D02-32G-EST2.2-U15.04",
              "192.168.40.49":"PC-I5650-U15.04",
              "192.168.40.7":"DELLR7-E5606-U15.04"
              }
         if client_ip in dic_mapping.keys():
             if bool(config.get("CLIENT","Platform_name")):
                 if config.get("CLIENT","Platform_name") != dic_mapping[client_ip]:
                      config.set("CLIENT", "Platform_name", "")
         if not bool(config.get("CLIENT","Platform_name")):
             if client_ip in dic_mapping.keys():
                 config.set("CLIENT", "Platform_name", dic_mapping[client_ip])
         # write changes back to the config file
         with open(path, "wb") as config_file:
             config.write(config_file)
    except Exception as e:
         print e
	 sys.exit(1)
      
#----------------------------------------------------------------------
if __name__ == "__main__":
     argcount = len(sys.argv)
     if argcount == 4:
	modify( sys.argv[1], sys.argv[2], sys.argv[3] )
     elif argcount == 16:
	modify_client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9],sys.argv[10], sys.argv[11],sys.argv[12],sys.argv[13],sys.argv[14], sys.argv[15])
