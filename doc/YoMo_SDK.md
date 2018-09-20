# YoMo SDK

## Build the sdk bootstrap

```bash
bitbake sdk-bootstrap
```

Publish your SDK boot strap

```bash
export SDK_BS_DIR="sdk-bootstrap"
mkdir -p ${SRV_DIR}/${SDK_BS_DIR}
export SDK_INSTALL_SCRIPT=$(basename $(ls tmp/deploy/sdk/x86_64-sdk-bootstrap-*.sh))
cp tmp/deploy/sdk/${SDK_INSTALL_SCRIPT} ${SRV_DIR}/${SDK_BS_DIR}
```

## Publish repositories config file

```bash
export YOUR_HTTP_SRV="your_http_server"
cat >${SRV_DIR}/${SDK_BS_DIR}/SDK-configuration.json<<EOF
{
    "repo":{
        "runtime":{
            "Name":"${ARCH}",
            "runtime":"http://${YOUR_HTTP_SRV}/${PUBDIR}/runtime/"
        },
        "sdk":{
            "sdk":"http://${YOUR_HTTP_SRV}/${PUBDIR}/nativesdk/"
        }
    }
 }
EOF
```

## Build SDK config files

```bash
bitbake sysroots-conf nativesdk-sysroots-conf -c install
```

Publish SDK config files:

```bash
cp tmp/work/x86_64-nativesdk-*-linux/nativesdk-sysroots-conf/0.1-r0/image/opt/*/*/sysroots/x86_64-*-linux/usr/share/sdk_default.json ${SRV_DIR}/${SDK_BS_DIR}
cp tmp/work/*/sysroots-conf/0.1-r0/image/usr/share/*_default.json ${SRV_DIR}/${SDK_BS_DIR}
```

## Init your SDK bootstrap

At first download and install the sdk-bootstrap

```bash
mkdir -p /xdt/sdk-config
cd /xdt/sdk-config
export BOOTSTRAP_INSTALL=/xdt/sdk-bootstrap
wget http://${YOUR_HTTP_SRV}/${SDK_BS_DIR}/${SDK_INSTALL_SCRIPT}
chmod a=x ./${SDK_INSTALL_SCRIPT}
sudo ./${SDK_INSTALL_SCRIPT} -d ${BOOTSTRAP_INSTALL} -y
```

Init your sdk-bootstrap:

```bash
export PATH=${BOOTSTRAP_INSTALL}/sysroots/x86_64-aglsdk-linux/usr/bin:$PATH
```

Note: You can add this line to your bachrc.

Or:

```bash
source ${BOOTSTRAP_INSTALL}/environment-setup-x86_64-*-linux
```

## Init your SDK

### Download repositories config files

```bash
cd /xdt/sdk-config
wget http://${YOUR_HTTP_SRV}/${SDK_BS_DIR}/SDK-configuration.json
wget http://${YOUR_HTTP_SRV}/${SDK_BS_DIR}/${ARCH}_default.json
wget http://${YOUR_HTTP_SRV}/${SDK_BS_DIR}/sdk_default.json
```

### Create your SDK

```bash
init-sdk-rootfs -i ${ARCH}_default.json -i SDK-configuration.json -i sdk_default.json -o /xdt/sdk-yomo
```

### Update your SDK

Init native sysroot:

```bash
cd /xdt/sdk-yomo/${ARCH}-sdk/
./dnf4Native install packagegroup-cross-canadian-*
```

=======> cd /xdt/sdk-yomo/myProject-sdk/

=======> pb avec génération ./dnf4Native cf init-sdk-rootfs.py

Native tool:

```bash
cd /xdt/sdk-yomo/${ARCH}-sdk/
./dnf4Native search cmake
./dnf4Native install nativesdk-cmake
```

Target tool:

```bash
cd /xdt/sdk-yomo/${ARCH}-sdk/
./dnf4Target search libglib-2.0-dev
```

### Use your SDK on AGL

```bash
cd /xdt/sdk-yomo/${ARCH}-sdk/
PKG="nativesdk-packagegroup-qt5-toolchain-host nativesdk-packagegroup-sdk-host packagegroup-cross-canadian-*"
./dnf4Native install ${PKG}
PKG="packagegroup-qt5-toolchain-target linux-libc-headers-dev libjson-c-dev af-binder-dev"
./dnf4Target install ${PKG}

git clone https://gerrit.automotivelinux.org/gerrit/apps/hvac
cd hvac
. /xdt/sdk-yomo/${ARCH}-sdk/env-init-SDK.sh
qmake
make
```
