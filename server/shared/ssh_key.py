#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Date    :   14/12/31 15:01:30
#   Desc    :
#

import os
import logging

import remote


def get_public_key():
    """
    Return a valid string ssh public key for the user executing caliper.
    If there's no DSA or RSA public key, create a DSA keypair with
    ssh-keygen and return it.

    : returns: a ssh public key
    :rtype: str
    """

    ssh_conf_path = os.path.expanduser('~/.ssh')

    dsa_public_key_path = os.path.join(ssh_conf_path, 'id_dsa.pub')
    dsa_private_key_path = os.path.join(ssh_conf_path, 'id_dsa')

    rsa_public_key_path = os.path.join(ssh_conf_path, 'id_rsa.pub')
    rsa_private_key_path = os.path.join(ssh_conf_path, 'id_rsa')

    has_dsa_keypair = (os.path.isfile(dsa_public_key_path) and
                            os.path.isfile(dsa_private_key_path))
    has_rsa_keypair = (os.path.isfile(rsa_public_key_path) and
                            os.path.isfile(rsa_private_key_path))

    if has_dsa_keypair:
        print "DSA keypair found, using it"
        public_key_path = dsa_public_key_path

    elif has_rsa_keypair:
        print "RSA keypair found, using it"
        public_key_path = rsa_public_key_path
    else:
        print "Neither RSA or DSA keypair found, creating DSA ssh key pair "
        os.system('ssh-keygen -t dsa -q -N "" -f %s' % dsa_private_key_path)
        public_key_path = dsa_public_key_path

    public_key = open(public_key_path, 'r')
    public_key_str = public_key.read()
    public_key.close()

    return public_key_str


def setup_ssh_key(hostname, user, password, port=22):
    """
    Setup up remote login in another server by using public key

    :param hostname: the server to login
    :type hostname: str
    :param user: user to login
    :type user: str
    :param password: password
    :type password: str
    :param port: port number
    :type port: int
    """
    logging.debug('Performing SSH key setup on %s:%d as %s.' %
                    (hostname, port, user))
    try:
        public_key = get_public_key()
        # remote_login is need to be realize
        session = remote.remote_login(client='ssh', host=hostname, port=port,
                                        username=user, portword=password,
                                        prompt=r'[$#%]')
        session.cmd_output('mkdir -p ~/.ssh')
        session.cmd_output('chmod 700 ~/.ssh')
        session.cmd_output("echo '%s' >> ~/.ssh/authorized_keys" % public_key)
        session.cmd_output('cmd 600 ~/.ssh/authorized_keys')
        logging.debug('SSH key setup complete.')
    except Exception as err:
        logging.debug('SSH key setup has failed: %s', err)
        try:
            session.close()
        except:
            pass
