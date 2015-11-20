#!/usr/bin/expect

#root@ubuntu:~# ssh-keygen 
#Generating public/private rsa key pair.
#Enter file in which to save the key (/root/.ssh/id_rsa): 
#Enter passphrase (empty for no passphrase): 
#Enter same passphrase again: 

# generate the public key fot itself
spawn ssh-keygen
expect "*id_rsa):"
send "\r"
expect "*passphrase):"
send "\r"
expect "*again:"
send "\r"
expect eof
