#!/bin/bash

# I want us to error out if we use an undefined variable, so we will catch errors.
set -u

#################### usplash functions start ####################################
# alias usplash_write to the 'true' command if we don't have usplash_write
type usplash_write > /dev/null 2>&1 || alias usplash_write="true"

# show the progress at status bar.
# $1 = 0-100
splash_progress(){
    usplash_write "PROGRESS $1"
    return 0
}
# display the text no matter whether verbose is set or not
splash_display(){
    echo "$@"
    usplash_write "TEXT-URGENT $@"
    return 0
}
# set the splash delay time
splash_delay(){
    usplash_write "TIMEOUT $1"
    return 0
}
####################### usplash functions end ###############################

splash_delay 200
splash_display 'INSTALL..........'

pre_scsi_disk_number=$( ls /sys/class/scsi_disk | wc -l)

splash_display 'Deleting Partition Table on /dev/sda...'
splash_delay 200
dd if=/dev/zero of=/dev/sda bs=512 count=2
sync
splash_progress 5
splash_delay 10

splash_display 'Creating New Partiton Table on /dev/sda...'
splash_delay 200
fdisk /dev/sda <<EOF
n
p
1
1
+1024M
n
p
2


a
1
w
EOF

sync
splash_progress 10
splash_delay 10

splash_display 'Formatting /dev/sda1 w/ ext2...'
splash_delay 200
mkfs.ext2 /dev/sda1
sync
splash_progress 20
splash_delay 10


splash_display 'Formatting /dev/sda2 w/ ext3...'
splash_delay 200
mkfs.ext3 /dev/sda2
sync
splash_progress 60
splash_delay 10

splash_display 'Mounting partitions...'
splash_delay 200
mkdir /tmp/boot
mount -o loop -t squashfs /tmp/install/bootfs.img /tmp/boot


mount /dev/sda2 /mnt
mkdir /mnt/boot
mount /dev/sda1 /mnt/boot
splash_progress 70
splash_delay 10

splash_display 'Copying system files onto hard disk drive...'
splash_delay 200
cp -v /tmp/install/rootfs.img /mnt/boot
cp -av /tmp/boot /mnt

/usr/sbin/grub-install --root-directory=/mnt /dev/sda
splash_progress 90
splash_delay 10

splash_display 'Unmounting partitions...'
splash_delay 200

umount /mnt/boot
umount /mnt
umount /tmp/boot
umount /tmp/install
splash_progress 95
splash_delay 10
sleep 1
splash_delay 6000
splash_display "Install Successfully"
splash_display "Unplug USB Key, System Will Reboot Automatically"

while [ $pre_scsi_disk_number = $(ls /sys/class/scsi_disk | wc -l) ]
do
    sleep 1
done

splash_progress 100
splash_delay 1

reboot -f
