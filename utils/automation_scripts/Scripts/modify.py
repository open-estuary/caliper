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
def modify(path, client_ip, server_ip, Platform_name):
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
         config.set("CLIENT", "Platform_name", Platform_name)
         # write changes back to the config file
         with open(path, "wb") as config_file:
             config.write(config_file)
    except Exception as e:
         print e
	 sys.exit(1)
      
#----------------------------------------------------------------------
if __name__ == "__main__":
     argcount = len(sys.argv)
     if argcount == 5:
	modify( sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
     elif argcount == 16:
	modify_client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9],sys.argv[10], sys.argv[11],sys.argv[12],sys.argv[13],sys.argv[14], sys.argv[15])
