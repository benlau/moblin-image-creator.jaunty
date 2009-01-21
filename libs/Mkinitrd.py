#!/usr/bin/python -tt
# vim: ai ts=4 sts=4 et sw=4

import os
import re
import shutil
import sys
import tempfile

import SDK
import mic_cfg

class Busybox(object):
    def __init__(self, cmd_path, bin_path):
        self.cmd_path = os.path.abspath(os.path.expanduser(cmd_path))
        self.bin_path = os.path.abspath(os.path.expanduser(bin_path))
        self.cmds = []

        # Extract the list of supported busybox commands
        #
        # This is far from ideal, but this method doesn't require
        # modifying the original Busybox RPM package and capturing
        # symlinks w/ a "make install" of the Busybox sources
        buf = ""
        flag = 0
        bf = os.popen(cmd_path)
        for line in bf:
            if (flag == 0):
                if re.search(r'^Currently defined functions:', line):
                    flag = 1
                continue
            else:
                # strip off the new-line & white-space 
                line = line.strip()
                # Delete all spaces inside the line
                line = re.sub(r'\s+', '', line)

                if line:
                    buf = buf + line

        buf = re.sub(r'busybox,', '', buf)
        self.cmds = buf.split(',')

    def create(self):
        if not os.path.isdir(self.bin_path):
            os.makedirs(self.bin_path)

        save_cwd = os.getcwd()
        os.chdir(self.bin_path)

        if not os.path.exists('busybox'):
            shutil.copy(self.cmd_path, 'busybox')

        for cmd in self.cmds:
            if not os.path.exists(cmd):    
                os.symlink("busybox", cmd)
        os.chdir(save_cwd)

def create(project, initrd_file, additional_files, target_path, fs_type='RAMFS'):
    """Function to create an initrd file"""
    initrd_file = os.path.abspath(os.path.expanduser(initrd_file))

    save_cwd = os.getcwd()
    # Create scratch area for creating files
    scratch_path = tempfile.mkdtemp('','pdk-', '/tmp')
    
    # Setup initrd directory tree
    bin_path = os.path.join(scratch_path, 'bin')

    # Create directories
    dirs = [ 'bin', 'boot', 'etc', 'dev', 'lib', 'mnt', \
             'proc', 'sys', 'sysroot', 'tmp', 'usr/bin' ]
    for dirname in dirs:
        os.makedirs(os.path.join(scratch_path, dirname))

    os.symlink('init', os.path.join(scratch_path, 'linuxrc'))
    os.symlink('bin', os.path.join(scratch_path, 'sbin'))

    # Setup Busybox in the initrd
    cmd_path = os.path.join(project.path, 'sbin/busybox')
    bb = Busybox(cmd_path, bin_path)
    bb.create()
    #Setup moblin-initramfs.cfg file
    shutil.copy(os.path.join(project.path, 'etc/moblin-initramfs.cfg'), os.path.join(scratch_path, 'etc'))
    # Setup init script
    names = os.listdir(os.path.join(project.platform.path, 'initramfs'))
    for name in names:
        shutil.copy(os.path.join(project.platform.path, 'initramfs', name), scratch_path)
    #Copy additional files - firmware, scripts etc
    if additional_files:
        for file_path in additional_files:
            file_path = file_path.rstrip()
            if os.path.exists(os.path.join(target_path, file_path)):
                folder_path = (os.path.join(scratch_path, file_path)).rsplit('/', 1)[0]
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                #print "Copying: %s to %s" % (os.path.join(target_path, file_path), os.path.join(scratch_path, file_path))
                shutil.copyfile(os.path.join(target_path, file_path), os.path.join(scratch_path, file_path))
    # Create the initrd image file
    os.chdir(scratch_path)

    if mic_cfg.config.get('general', 'package_manager') == 'apt':
        cmd_string = "find -print | cpio --quiet -H newc -o | gzip -9 -c > " + initrd_file
    if mic_cfg.config.get('general', 'package_manager') == 'yum':
        cmd_string = "find -print | cpio --quiet -c -o | gzip -9 -c > " + initrd_file
    os.system(cmd_string)
    os.chdir(save_cwd)

    # Clean-up and remove scratch area
    shutil.rmtree(scratch_path)

class Callback:
    def iteration(process):
        return

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >> sys.stderr, "USAGE: %s PROJECT INITRD_FILE" % (sys.argv[0])
        sys.exit(1)

    project_name = sys.argv[1]
    initrd_file = sys.argv[2]

    proj = SDK.SDK(Callback()).projects[project_name]

    create(proj, initrd_file)
