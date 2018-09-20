SUMMARY = "rootfs configuration"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

BBCLASSEXTEND = "nativesdk"

CONFNAME = "runtime_conf"
CONFNAME_class-nativesdk = "sdk_conf"

do_install() {
    mkdir -p ${D}${datadir}/
    cat >${D}${datadir}/${MACHINE_ARCH}_default.json<<'EOF'
{
    "runtime_conf":{
        "TUNE_PKGARCH":   "${TUNE_PKGARCH}",
        "TARGET_VENDOR":  "${TARGET_VENDOR}",
        "TARGET_SYS":     "${TARGET_SYS}",
        "DISTRO":         "${DISTRO}",
        "DISTRO_CODENAME":"${DISTRO_CODENAME}",
        "MACHINE_ARCH":   "${MACHINE_ARCH}",
        "ALL_MULTILIB_PACKAGE_ARCHS":"${ALL_MULTILIB_PACKAGE_ARCHS}"
    }
 }
EOF
#We need a space for the last bracket to ovoid a parse error.
}

do_install_class-nativesdk() {
    mkdir -p ${D}${datadir}/
    cat >${D}${datadir}/sdk_default.json<<'EOF'
{
    "sdk_conf":{
        "TUNE_PKGARCH":   "${TUNE_PKGARCH}",
        "SDK_ARCH":       "${SDK_ARCH}",
        "HOST_SYS":       "${HOST_SYS}",
        "SDK_VENDOR":     "${SDK_VENDOR}",
        "SDK_VERSION":    "${SDK_VERSION}",
        "SDKPATH":        "${SDKPATH}",
        "SDK_OS":         "${SDK_OS}",
        "DISTRO":         "${DISTRO}",
        "DISTRO_CODENAME":"${DISTRO_CODENAME}",
        "MACHINE_ARCH":   "${MACHINE_ARCH}",
        "ALL_MULTILIB_PACKAGE_ARCHS":"${ALL_MULTILIB_PACKAGE_ARCHS}"
    }
 }
EOF
#We need a space for the last bracket to ovoid a parse error.
}

FILES_${PN} += "${datadir}/*.json"
