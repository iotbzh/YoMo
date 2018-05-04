SUMMARY = "init sdk rootfs"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRC_URI = " \
            file://init-sdk-rootfs.py \
            "

RDEPENDS_${PN} = "dnf"

BBCLASSEXTEND = "nativesdk"
S = "${WORKDIR}"

do_install() {
    mkdir -p ${D}${bindir}

    #Init SDK tool
    cp ${S}/init-sdk-rootfs.py ${D}${bindir}/init-sdk-rootfs

    #Clean sysroot relative links
    cp $(which sysroot-relativelinks.py) ${D}${bindir}

    #SDK post install tools
    cp ${COREBASE}/meta/files/toolchain-shar-relocate.sh ${D}${bindir}
    cp ${COREBASE}/scripts/relocate_sdk.py ${D}${bindir}

    # Replace the ##DEFAULT_INSTALL_DIR## with the correct pattern.
    # Escape special characters like '+' and '.' in the SDKPATH
    escaped_sdkpath=$(echo ${SDKPATHNATIVE} |sed -e "s:[\+\.]:\\\\\\\\\0:g")
    sed -i -e "s:##DEFAULT_INSTALL_DIR##:$escaped_sdkpath:" ${D}${bindir}/relocate_sdk.py

    chmod a+x ${D}${bindir}/toolchain-shar-relocate.sh
    chmod a+x ${D}${bindir}/relocate_sdk.py

}

FILES_${PN} += "${bindir}/*"
