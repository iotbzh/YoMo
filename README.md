# SDK Boostrap 

## build AGL-SDK-bootstrap

Add "meta-agl-sdkbootstrap" to your 

```
BBLAYERS =+ " ${AGL_SDK_managed}/meta-agl-sdkbootstrap"
```

```bash
bitbake AGL-SDK-bootstrap
```

## Install AGL-SDK-bootstrap (18M)

```bash
cp ${WORK_DIR}/build_m3ulcb/tmp/deploy/sdk/x86_64-AGL-SDK-bootstrap-4.90.0+snapshot-*.sh ./
```

ou

```bash
wget -O x86_64-AGL-SDK-bootstrap-4.90.0+snapshot.sh http://repo.iot.bzh/SDK-bootstrap/latest/x86_64-AGL-SDK-bootstrap-4.90.0+snapshot.sh
```

## Init AGL-SDK-bootstrap on target

Install AGL SDK
```bash
chmod a+x ./x86_64-AGL-SDK-bootstrap-4.90.0+snapshot*.sh
export XDT_SDK_BOOTSTRAP=/usr/share/sdk-bootstrap
./x86_64-AGL-SDK-bootstrap-4.90.0+snapshot*.sh -y -d ${XDT_SDK_BOOTSTRAP}
```

Configure env

```bash
. ${XDT_SDK_BOOTSTRAP}/environment-setup-x86_64-aglsdk-linux
```

ou

```bash
export PATH=${XDT_SDK_BOOTSTRAP}/sysroots/x86_64-aglsdk-linux/usr/bin:$PATH 
```

Init SDK

```bash
wget -O AGL-m3ulcb-master.sdk http://repo.iot.bzh/SDK-conf/AGL-m3ulcb-master.sdk
sudo chmod a+rwx -R ${XDT_DIR}
init-SDK-rootfs -i AGL-m3ulcb-master.sdk -o ${XDT_SDK}
```

## Init Repositories

### SDK Host package 

```bash
${XDT_SDK}/m3ulcb-sdk/dnf4Native makecache
```

### SDK Target package 

```bash
${XDT_SDK}/m3ulcb-sdk/dnf4Target makecache
```

## Package installation

### Minimal installation

#### Install SDK Host package 

```bash
PKG="nativesdk-packagegroup-sdk-host packagegroup-cross-canadian-m3ulcb"
${XDT_SDK}/m3ulcb-sdk/dnf4Native install ${PKG}
```

### Mostly full install

#### Install SDK Host package 

```bash
PKG="nativesdk-packagegroup-qt5-toolchain-host nativesdk-packagegroup-sdk-host nativesdk-nspr-dev nativesdk-zlib nativesdk-xz packagegroup-cross-canadian-m3ulcb nativesdk-nss-dev"
${XDT_SDK}/m3ulcb-sdk/dnf4Native install ${PKG}
```

#### Install SDK Target package 

```bash
PKG="packagegroup-core-eclipse-debug packagegroup-agl-demo-platform dnf pciutils-dev rpm pango-dev libcairo-dev kernel-module-pvrsrvkm omx-user-module pulseaudio-dev kernel-module-vspm-if kernel-module-vspm packagegroup-qt5-toolchain-target libssp-dev gconf-dev libdrm-dev packagegroup-core-tools-profile kernel-module-vsp2 psplash packagegroup-agl-devel kernel-dev screen nss-dev packagegroup-core-standalone-sdk-target packagegroup-core-tools-debug packagegroup-core-ssh-openssh mc kernel-modules linux-libc-headers-dev libjson-c-dev af-binder-dev"
${XDT_SDK}/m3ulcb-sdk/dnf4Target install ${PKG}
```
