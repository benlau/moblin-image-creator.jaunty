#!/usr/bin/python -tt
# vim: ai ts=4 sts=4 et sw=4

#    Copyright (c) 2007 Intel Corporation
#
#    This program is free software; you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the Free
#    Software Foundation; version 2 of the License
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#    or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#    for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc., 59
#    Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import ConfigParser
import os
import re
import sys

import fsets

class Platform(object):
    """
    The SDK is composed of a collection of platforms, where this class
    represents a specific platform.  A platform provides:
    - a list of packages to install directly into the platform (i.e. to use as
      a jailroot to isolate building target binaries from the host
      distribution)
    - a set of fsets that can be installed into a target
    """
    def __init__(self, sdk_path, name):
        self.sdk_path = os.path.abspath(os.path.expanduser(sdk_path))
        self.name = name
        self.path = os.path.join(self.sdk_path, 'platforms', self.name)
        # instantiate all fsets
        self.fset = fsets.FSet()
        fset_path = os.path.join(self.path, 'fsets')
        for filename in os.listdir(fset_path):
            self.fset.addFile(os.path.join(fset_path, filename))
        # determine what packages additional packages need to be installed
        # in the buildroot roostrap
        self.buildroot_extras = ""
        config = open(os.path.join(self.path, 'buildroot_extras'))
        for line in config:
            # Ignore lines beginning with '#'
            if not re.search(r'^\s*#', line):
                for p in line.split():
                    self.buildroot_extras += p + ','
        config.close()
        # determine what packages need to be installed in the buildroot
        # (outside the rootstrap archive)
        self.buildroot_packages = []
        config = open(os.path.join(self.path, 'buildroot.packages'))
        for line in config:
            # Ignore lines beginning with '#'
            if not re.search(r'^\s*#', line):
                for p in line.split():
                    self.buildroot_packages.append(p)
        config.close()
        # determine what mirror to use for the buildroot
        print os.path.join(self.path, 'buildroot_mirror')
        if os.path.isfile(os.path.join(self.path, 'buildroot_mirror')):
            t = open(os.path.join(self.path, 'buildroot_mirror'))
            self.buildroot_mirror = t.readline()
            t.close()
        else:
            self.buildroot_mirror = "http://archive.ubuntu.com/ubuntu/"
        # determine what codename to use for the buildroot mirror
        if os.path.isfile(os.path.join(self.path, 'buildroot_codename')):
            t = open(os.path.join(self.path, 'buildroot_codename'))
            self.buildroot_codename = t.readline()
            t.close()
        else:
            self.buildroot_codename = "gutsy"
        # determine what mirror to use for the target
        if os.path.isfile(os.path.join(self.path, 'target_mirror')):
            t = open(os.path.join(self.path, 'target_mirror'))
            self.target_mirror = t.readline()
            t.close()
        else:
            self.target_mirror = "http://archive.ubuntu.com/ubuntu/"
        # determine what codename to use for the buildroot mirror
        if os.path.isfile(os.path.join(self.path, 'target_codename')):
            t = open(os.path.join(self.path, 'target_codename'))
            self.target_codename = t.readline()
            t.close()
        else:
            self.target_codename = "gutsy"
        # determine default kernel cmdline options
        self.usb_kernel_cmdline = ''
        self.hd_kernel_cmdline = ''
        config = open(os.path.join(self.path, 'usb_kernel_cmdline'), 'r')
        for line in config:
            if not re.search(r'^\s*#',line):
                self.usb_kernel_cmdline += line + ' '
        config.close()
        config = open(os.path.join(self.path, 'hd_kernel_cmdline'), 'r')
        for line in config:
            if not re.search(r'^\s*#',line):
                self.hd_kernel_cmdline += line + ' '
        config.close()
        config_file = os.path.expanduser("~/.image-creator/platforms.cfg")
        if os.path.isfile(config_file):
            config = ConfigParser.SafeConfigParser()
            config.read(config_file)
            if config.has_section(name):
                for cfg_option in [ 'buildroot_mirror', 'buildroot_codename',
                    'target_mirror', 'target_codename' ]:
                    if config.has_option(name, cfg_option):
                        setattr(self, cfg_option, config.get(name, cfg_option))

    def __str__(self):
        return ("<Platform Object: \n\tname=%s, \n\tfset=%s, \n\tbuildroot_packages=%s>\n" %
                (self.name, self.fset, self.buildroot_packages))

    def __repr__(self):
        return "Platform( %s, '%s')" % (self.sdk_path, self.name)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print Platform('/usr/share/pdk', p)
