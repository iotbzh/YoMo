SUMMARY = "sdk repo manager"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRC_URI = " \
            file://update-sdk-repo.py \
            "

RDEPENDS_${PN} ="createrepo-c build-compare"

DEPENDS_class-native ="createrepo-c build-compare"

BBCLASSEXTEND = "native nativesdk"
S = "${WORKDIR}"

do_install() {
    mkdir -p ${D}${bindir}

    #Init SDK tool
    cp ${S}/update-sdk-repo.py ${D}${bindir}/update-sdk-repo

}


FILES_${PN} += "${bindir}/* \
               "
