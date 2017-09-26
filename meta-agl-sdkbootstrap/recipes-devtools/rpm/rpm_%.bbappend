FILESEXTRAPATHS_append := ":${THISDIR}/${PN}"

SRC_URI_append_class-nativesdk = " file://0001-Remove-pre-post-install-script-for-AGL-SDK.patch"


# --sysconfdir prevents rpm from attempting to access machine-specific configuration in sysroot/etc; we need to have it in rootfs
#
# --localstatedir prevents rpm from writing its database to native sysroot when building images
#
# Also disable plugins, so that rpm doesn't attempt to inhibit shutdown via session dbus
EXTRA_OECONF_append_class-nativesdk = " --sysconfdir=/etc --localstatedir=/var --disable-plugins"


do_install_append_class-nativesdk () {
	rm -fr  ${D}/var
}
