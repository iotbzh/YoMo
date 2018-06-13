# This allow reuse of Qt paths
inherit qmake5_paths

do_install_append_class-nativesdk() {

    # Generate a qt.conf file to be deployed with the SDK

    qtconf=${D}${OE_QMAKE_PATH_BINS}/qt.conf
    touch $qtconf
    echo '[Paths]' >> $qtconf
    echo 'Prefix = ${OE_QMAKE_PATH_PREFIX}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Headers = ${OE_QMAKE_PATH_QT_HEADERS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Libraries = ${OE_QMAKE_PATH_LIBS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'ArchData = ${OE_QMAKE_PATH_QT_ARCHDATA}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Data = ${OE_QMAKE_PATH_QT_DATA}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Binaries = ${OE_QMAKE_PATH_QT_BINS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'LibraryExecutables = ${OE_QMAKE_PATH_LIBEXECS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Plugins = ${OE_QMAKE_PATH_PLUGINS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Imports = ${OE_QMAKE_PATH_IMPORTS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Qml2Imports = ${OE_QMAKE_PATH_QML}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Translations = ${OE_QMAKE_PATH_QT_TRANSLATIONS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Documentation = ${OE_QMAKE_PATH_QT_DOCS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Settings = ${OE_QMAKE_PATH_QT_SETTINGS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Examples = ${OE_QMAKE_PATH_QT_EXAMPLES}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'Tests = ${OE_QMAKE_PATH_QT_TESTS}' |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'HostPrefix = ${SDKPATHNATIVE}' >> $qtconf
    echo 'HostData = #SDKTARGETSYSROOT#${OE_QMAKE_PATH_QT_ARCHDATA}'  |sed "s@${SDKPATHNATIVE}@@" >> $qtconf
    echo 'HostBinaries = ${OE_QMAKE_PATH_HOST_BINS}' >> $qtconf
    echo 'HostLibraries = ${OE_QMAKE_PATH_LIBS}' >> $qtconf
    echo 'Sysroot = #SDKTARGETSYSROOT#' >> $qtconf
}


#FILES_${PN}-tools += "${SiDKPATHNATIVE}${OE_QMAKE_PATH_HOST_BINS}/qt.conf"


