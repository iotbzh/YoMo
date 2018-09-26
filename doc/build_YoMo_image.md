
# Configure and build an image

setup your working directory:

```bash
WORKDIR="/xdt/workdir-agl-yomo"
mkdir -p ${WORKDIR}
mkdir -p "${WORKDIR}/meta" "${WORKDIR}/build"
```

## For AGL project

> At first you need to initialize your AGL project source.
[Documentation](http://docs.automotivelinux.org/docs/getting_started/en/dev/reference/source-code.html)

Here a quick documentation (but read the official documentation first)

```bash
mkdir -p ~/bin
export PATH=~/bin:$PATH
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
chmod a+x ~/bin/repo
```

```bash
rm -rf ${WORKDIR}/meta/*
cd ${WORKDIR}/meta
repo init -u https://gerrit.automotivelinux.org/gerrit/AGL/AGL-repo
repo sync
git clone https://github.com/iotbzh/YoMo.git
```

Note : You can choose another source release [Here](http://docs.automotivelinux.org/docs/getting_started/en/dev/reference/source-code.html#download-source)

### init your build directory for AGL

```bash
MACHINE="m3ulcb"
cd "${WORKDIR}/build"
source ${WORKDIR}/meta/meta-agl/scripts/aglsetup.sh -m ${MACHINE} -b yomo agl-devel agl-demo agl-netboot agl-appfw-smack agl-localdev
. agl-init-build-env
```

## For Yocto Project

> At first you need to initialize your yocto project source.

```bash
rm -rf ${WORKDIR}/meta/*
cd ${WORKDIR}/meta
git clone -b sumo git://git.yoctoproject.org/poky.git
git clone https://github.com/iotbzh/YoMo.git
```

### init your build directory For Yocto

```bash
cd "${WORKDIR}/build"
source ${WORKDIR}/meta/poky/oe-init-build-env yomo
```

## Configure your Project

> Add meta-yomo  to conf/bblayers.conf

* Edit your file

```bash
vim ${WORKDIR}/build/yomo/conf/bblayers.conf
```

* And add line

```bash
BBLAYERS += "${WORKDIR}/meta/YoMo/meta-yomo"
```

Note: You must replace ${WORKDIR} by your path ${WORKDIR}/meta

* If you use meta-qt5 add:

```bash
BBLAYERS += "${WORKDIR}/meta/YoMo/meta-qt5-yomo"
```

## Build your project

### For AGL

```bash
cd "${WORKDIR}/build/yomo"
source agl-init-build-env
bitbake agl-demo-platform-crosssdk -k
```

### For Yocto

```bash
. ${WORKDIR}/meta/poky/oe-init-build-env ${WORKDIR}/build/yomo
bitbake core-image-sato
```

And build your SDK RPM

```bash
bitbake core-image-sato -c populate_sdk
```
