SUMMARY = "Yocto repo manager"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRC_URI = " \
            file://repo-manager.py \
            "

RDEPENDS_${PN} ="createrepo-c build-compare"

DEPENDS_class-native ="createrepo-c build-compare"

BBCLASSEXTEND = "native nativesdk"
S = "${WORKDIR}"

do_install() {
    mkdir -p ${D}${bindir}
    cp ${S}/repo-manager.py ${D}${bindir}/repo-manager
}

FILES_${PN} += "${bindir}/repo-manager"
