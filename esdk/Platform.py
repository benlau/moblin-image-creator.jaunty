#!/usr/bin/python -tt

import os, re, sys, unittest
import FSet

class Platform(object):
    """
    The SDK is composed of a collection of platforms, where this class
    represents a specific platform.  A platform provides:
    - a list of packages to install directly into the platform (i.e. to use as
      a jailroot to isolate building target binaries from the host
      distribution)
    - a set of fsets that can be installed into a target
    - a list of yum repositories that are used to install the fsets

    """
    def __init__(self, sdk_path, name):
        self.sdk_path = os.path.abspath(os.path.expanduser(sdk_path))
        self.name = name
        self.path = os.path.join(self.sdk_path, 'platforms', self.name)
        # instantiate all fsets
        self.fset = FSet.FSet()
        fset_path = os.path.join(self.path, 'fsets')
        for filename in os.listdir(fset_path):
            self.fset.addFile(os.path.join(fset_path, filename))
        # instantiate all target repos
        self.target_repos = []
        target_repo_path = os.path.join(self.path, 'target_repos')
        for repo in os.listdir(target_repo_path):
            self.target_repos.append(os.path.join(target_repo_path, repo))
        # instantiate all buildroot repos
        self.buildroot_repos = []
        build_repo_path = os.path.join(self.path, 'buildroot_repos')
        for repo in os.listdir(build_repo_path):
            self.buildroot_repos.append(os.path.join(build_repo_path, repo))
        # determine what packages need to be installed in the jailroot
        self.jailroot_packages = []
        config = open(os.path.join(self.path, 'jailroot.packages'))
        for line in config:
            # Ignore lines beginning with '#'
            if not re.search(r'^\s*#', line):
                for p in line.split():
                    self.jailroot_packages.append(p)
        config.close()

    def __str__(self):
        return ("<Platform Object: \n\tname=%s, \n\tfset=%s, \n\ttarget_repos=%s\n\tjailroot_packages=%s>\n" %
                (self.name, self.fset, self.target_repos, self.jailroot_packages))

    def __repr__(self):
        return "Platform( %s, '%s')" % (self.sdk_path, self.name)

class TestPlatform(unittest.TestCase):
    def testInstantiate(self):
        platform = Platform('/usr/share/esdk', 'donley')
    def testStrRepr(self):
        platform = Platform('/usr/share/esdk', 'donley')
        temp = platform.__str__()
        temp = platform.__repr__()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        unittest.main()
    for p in sys.argv[1:]:
        print Platform('/usr/share/esdk', p)