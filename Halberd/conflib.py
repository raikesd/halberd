# -*- coding: iso-8859-1 -*-

# Copyright (C) 2004 Juan M. Bello Rivas <rwx@synnergy.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


"""Configuration file management module.

Halberd uses configuration files to store relevant information needed for
certain protocols (SSL) or modes of operation (proxy, distributed
client/server, etc.).

This module takes care of reading and writing configuration files.

@var default_cfgfile: Path and name of the configuration file used by default.
@type default_cfgfile: C{str}

@var default_proxy_port: Default TCP port to listen when acting as a proxy.
@type default_proxy_port: C{int}

@var default_rpc_port: Default TCP port to listen when acting as an RPC server.
@type default_rpc_port: C{int}
"""

__revision__ = '$Id: conflib.py,v 1.7 2004/03/03 09:38:17 rwx Exp $'


import os
import ConfigParser


default_proxy_port = 8080
default_rpc_port = 2323

default_conf = r"""
# ============================================================================
# halberd configuration file.
# ============================================================================

[proxy]

address:
port: 8080

[rpcserver]

address:
port: 2323

[rpcclient]

# Example:
#   servers: 10.10.10.1:2323, 10.10.10.2:2323, 172.26.0.77:2323
servers:

[ssl]

keyfile: halberd.pkey
certfile: halberd.pem
"""


class InvalidConfFile(Exception):
    """Invalid configuration file.
    """


class ConfOptions:
    """Structure holding information obtained from a configuration file.
    """
    proxy_serv_addr = ()
    rpc_serv_addr = ()
    rpc_servers = []


class ConfReader:
    """Takes care of turning configuration files into meaningful information.
    """

    def __init__(self):
        self.__dict = {}
        self.__conf = None

        self.confparser = ConfigParser.RawConfigParser()

    def open(self, fname):
        """Opens the configuration file.

        @param fname: Pathname to the configuration file.
        @type fname: C{str}

        @raise InvalidConfFile: In case the passed file is not a valid one.
        """
        self.__conf = open(os.path.expanduser(fname), 'r')
        try:
            self.confparser.readfp(self.__conf, fname)
        except ConfigParser.MissingSectionHeaderError, msg:
            raise InvalidConfFile, msg

    def close(self):
        """Release the configuration file's descriptor.
        """
        if self.__conf:
            self.__conf.close()


    def _getAddr(self, sectname, default_port):
        """Read a network address from the given section.
        """
        section = self.__dict[sectname]
        addr = section.get('address', '')
        try:
            port = int(section.get('port', default_port))
        except ValueError:
            port = default_port

        return (addr, port)

    def parse(self):
        """Parses the configuration file.
        """
        assert self.__conf, 'The configuration file is not open'

        options = ConfOptions()

        # The orthodox way of doing this is via ConfigParser.get*() but those
        # methods lack the convenience of dict.get. While another approach
        # could be to subclass ConfigParser I think it's overkill for the
        # current situation.
        for section in self.confparser.sections():
            sec = self.__dict.setdefault(section, {})
            for name, value in self.confparser.items(section):
                sec.setdefault(name, value)

        if self.__dict.has_key('proxy'):
            options.proxy_serv_addr = self._getAddr('proxy',
                                                    default_proxy_port)

        if self.__dict.has_key('rpcserver'):
            options.rpc_serv_addr = self._getAddr('rpcserver',
                                                  default_rpc_port)

        try:
            rpc_servers = self.__dict['rpcclient']['servers']
            rpc_servers = [server.strip() for server in rpc_servers.split(',')\
                                          if server]
        except KeyError:
            rpc_servers = []

        options.rpc_servers = rpc_servers

        return options

    def writeDefault(self, conf_file):
        """Write a bare-bones configuration file

        @param conf_file: Target file where the default conf. will be written.
        @type conf_file: C{str}
        """
        assert conf_file and isinstance(conf_file, basestring)

        conf_fp = open(conf_file, 'w')
        conf_fp.write(default_conf)
        conf_fp.close()


    def __del__(self):
        self.close()


# vim: ts=4 sw=4 et
