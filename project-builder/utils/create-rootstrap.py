#!/usr/bin/python -tt
# vim: ai ts=4 sts=4 et sw=4

import sys, tempfile, subprocess, shutil, os, stat, socket, time

class Callback:
    def iteration(self, process):
        return

def create_devices(path):
        devices = [
            # name, major, minor, mode
            ('console', 5, 1, (0600 | stat.S_IFCHR)),
            ('null',    1, 3, (0666 | stat.S_IFCHR)),
            ('random',  1, 8, (0666 | stat.S_IFCHR)),
            ('urandom', 1, 9, (0444 | stat.S_IFCHR)),
            ('zero',    1, 5, (0666 | stat.S_IFCHR)),
        ]
        for device_name, major, minor, mode in devices:
            device_path = os.path.join(path, 'dev', device_name)
            device = os.makedev(major, minor)
            os.mknod(device_path, mode, device)
            # Seems redundant, but mknod doesn't seem to set the mode to
            # what we want :(
            os.chmod(device_path, mode)

def init_rpm_base(path, repos):
    for dirname in [ 'proc', 'var/log', 'var/lib/rpm', 'dev', 'etc/yum.repos.d' ]:
        os.makedirs(os.path.join(path, dirname))
    target_etc = os.path.join(path, "etc")
    for filename in [ 'hosts', 'resolv.conf' ]:
        shutil.copy(os.path.join('/etc', filename), target_etc)
        yumconf = open(os.path.join(target_etc, 'yum.conf'), 'w')
        print >> yumconf, """\
[main]
cachedir=/var/cache/yum
keepcache=0
debuglevel=2
logfile=/var/log/yum.log
pkgpolicy=newest
distroverpkg=redhat-release
tolerant=1
exactarch=1
obsoletes=1
gpgcheck=0
plugins=1
metadata_expire=1800
"""
        yumconf.close()
        for repo in repos:
            shutil.copy(repo, os.path.join(target_etc, 'yum.repos.d'))
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print >> sys.stderr, "USAGE: %s PLATFORM_DIR" % (sys.argv[0])
        sys.exit(1)
        
    platform_dir = sys.argv[1]
    platform_name = os.path.basename(platform_dir)
    repos = []
    rpath = os.path.join(platform_dir, 'buildroot_repos')
    for r in os.listdir(rpath):
        repos.append(os.path.join(rpath, r))
    
    path = tempfile.mkdtemp()
    init_rpm_base(path, repos)
    create_devices(path)

    # create a build timestamp file
    buildstamp = open(os.path.join(path, 'etc', 'buildstamp'), 'w')
    print >> buildstamp, "%s-%s" % (socket.gethostname(), time.strftime("%d-%m-%Y %H:%M:%S %Z"))
    buildstamp.close()

    # install yum inside the project using the host tools
    cmd = 'yum -y --installroot=%s install yum' % path
    proc = subprocess.Popen(cmd.split(), stderr = subprocess.PIPE)
    if proc.wait() != 0:
        print >> sys.stderr, "ERROR: Unable to create rootstrap!"
        for line in proc.stderr:
            print line.strip()
            sys.exit(1)

    # Create the rootstrap archive file
    cmd = "tar -jcpvf %s/rootstrap.tar.bz2 -C %s ." % (platform_dir, path)
    proc = subprocess.Popen(cmd.split(), stderr = subprocess.PIPE)
    if proc.wait() != 0:
        print >> sys.stderr, "ERROR: Unable to create rootstrap!"
        for line in proc.stderr:
            print line.strip()
            sys.exit(1)

    # cleanup the temporary project filesystem
    shutil.rmtree(path)