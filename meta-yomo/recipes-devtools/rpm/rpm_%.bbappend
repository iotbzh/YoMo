FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI_append_class-nativesdk = " \
    file://0001-Remove-pre-post-install-script-for-sdk.patch \
    file://0001-Fix-path-install-for-SDK-package-installation.patch \
    "

EXTRA_OECONF_append_class-nativesdk = " --sysconfdir=/etc --localstatedir=/var --disable-plugins"

do_install_append_class-nativesdk() {
    rm -rf ${D}/var
}
