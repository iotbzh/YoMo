FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_class-nativesdk = " \
    file://0001-Remove-pre-post-install-script-for-sdk.patch \
    file://0001-Fix-path-install-for-SDK-package-installation.patch.sumo \
    "

EXTRA_OECONF_append_class-nativesdk = " --sysconfdir=/etc --localstatedir=/var --disable-plugins"

do_patch_append_class-nativesdk() {
    bb.build.exec_func('do_extra_patch', d)
}

do_extra_patch () {
	if [[ ${PV} > '4.14' ]] ; then 
		cd ${S};
		patch -p1 < ${WORKDIR}/0001-Fix-path-install-for-SDK-package-installation.patch.sumo;
	fi;
}

do_install_append_class-nativesdk() {
    rm -rf ${D}/var
}
