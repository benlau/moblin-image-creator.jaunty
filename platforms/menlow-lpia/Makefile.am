PNAME = menlow-lpia

fsetsdir = ${pkgdatadir}/platforms/${PNAME}/fsets
fsets_DATA = \
	fsets/base.fset

platformdir = ${pkgdatadir}/platforms/${PNAME}
platform_SCRIPTS = \
	../common-apt/install.sh \
	../common-apt/nand.sh

platform_DATA = \
	../common-apt/exclude

initramfsdir = ${pkgdatadir}/platforms/${PNAME}/initramfs
initramfs_SCRIPTS = \
	../common-apt/initramfs/cd \
	../common-apt/initramfs/disk \
	../common-apt/initramfs/nand \
	../common-apt/initramfs/usb

initramfs_DATA = \
	initramfs/initramfs.conf \
	initramfs/modules \
	initramfs/usplash.conf

initramfs_hooksdir = ${pkgdatadir}/platforms/${PNAME}/initramfs/hooks
initramfs_hooks_SCRIPTS = \
	../common-apt/initramfs/hooks/mobile

initramfs_scriptsdir = ${pkgdatadir}/platforms/${PNAME}/initramfs/scripts
initramfs_scripts_DATA = 

sourcesdir = ${pkgdatadir}/platforms/${PNAME}/sources
sources_DATA = \
	sources/moblin.org.list \
	sources/ubuntu-gutsy-src.list
