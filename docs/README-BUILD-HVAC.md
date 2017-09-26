# Build test on HVAC

## Config

 Config your SDK env

## Install SDK package

```bash
PKG="nativesdk-packagegroup-qt5-toolchain-host nativesdk-packagegroup-sdk-host packagegroup-cross-canadian-m3ulcb" 
${XDT_SDK}/m3ulcb-sdk/dnf4Native install ${PKG}

PKG="packagegroup-qt5-toolchain-target linux-libc-headers-dev libjson-c-dev af-binder-dev"
${XDT_SDK}/m3ulcb-sdk/dnf4Target install ${PKG}
```


## Prepare source

```bash
git clone https://gerrit.automotivelinux.org/gerrit/apps/hvac
```

## build package

```bash

cd hvac
. ${XDT_SDK}/m3ulcb-sdk/env-init-SDK.sh
qmake
make
```
