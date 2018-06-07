# repository manager

## init project

> At first you need to initial your yocto project source.

```bash
mkdir -p "${WORKDIR}/meta" "${WORKDIR}/build"
cd ${WORKDIR}/meta
git clone -b sumo git://git.yoctoproject.org/poky.git
git clone https://github.com/iotbzh/YoMo.git
```

* for AGL project: [Here](http://docs.automotivelinux.org/docs/getting_started/en/dev/reference/source-code.html)

## Build

> init your build directoryash

```bash
cd "${WORKDIR}/build"
source ../meta/poky/oe-init-build-env yomo
```

* for AGL project: [Here](http://docs.automotivelinux.org/docs/getting_started/en/dev/reference/source-code.html)

>Add meta-yomo  to conf/bblayers.conf

* Edit your file

```bash
vim conf/bblayers.conf
```

* And add

```bash
BBLAYERS += "${WORKDIR}/meta/YoMo/meta-yomo"
```

Note: You must replace ${WORKDIR} by your path

* Build an image

```bash
bitbake core-image-sato
```

And build your SDK RPM

```bash
bitbake core-image-sato -c populate_sdk
```

* for AGL project:

```bash
bitbake agl-demo-platform-crosssdk
```

## Build yocto-repo-manager

### HTTP server

> You need to have a http server to serve your rpm repositories

For this documentation, we are going to use an Apache server.

But feel free to use your own HTTP server.

#### Install Apache server

For debian:

```bash
sudo apt-get install apache2
```

#### Create certificat

For HTTPS, you need to have a certificat.

```bash
openssl req -new -x509 -days 365 -nodes -out /etc/ssl/certs/yomo.crt -keyout /etc/ssl/private/yomo.key
```
output:

```bash
Generating a 2048 bit RSA private key
.................+++
.............+++
writing new private key to 'yomo.key'
-----
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:FR
State or Province Name (full name) [Some-State]:France
Locality Name (eg, city) []:Vannes
Organization Name (eg, company) [Internet Widgits Pty Ltd]:IoT.bzh
Organizational Unit Name (eg, section) []:IoTVannes
Common Name (e.g. server FQDN or YOUR name) []:XXXX
Email Address []:ronan.lemartret@iot.bzh
```

```bash
sudo chmod 440 /etc/ssl/certs/yomo.crt
```

#### Configure apache server

```bash
export USER_EMAIL=ronan.lemartret@iot.bzh
export SRV_DIR=/home/devel/share/http_svr/data
export SRV_LOG=/home/devel/share/http_svr/log

sudo mkdir -p ${SRV_DIR} ${SRV_LOG}

sudo bash -c "cat << EOF > /etc/apache2/sites-available/http_yomo.conf
<VirtualHost *:80>
    ServerAdmin ${USER_EMAIL}
    ServerName http_yomo
    DocumentRoot ${SRV_DIR}
    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>
    <Directory ${SRV_DIR}>
        Options Indexes MultiViews
        AllowOverride None
        Require all granted
    </Directory>
    ErrorLog ${SRV_LOG}/error.log
    LogLevel warn
</VirtualHost>
EOF"

sudo bash -c "cat << EOF > /etc/apache2/sites-available/https_yomo.conf
<VirtualHost *:443>
    ServerAdmin ${USER_EMAIL}
    ServerName https_yomo
    DocumentRoot ${SRV_DIR}
    <Directory />
        SSLRequireSSL
        Options FollowSymLinks
        AllowOverride None
    </Directory>

  ServerSignature Off
  LogLevel info

  SSLEngine on
  SSLCertificateFile /etc/ssl/certs/yomo.crt
  SSLCertificateKeyFile /etc/ssl/private/yomo.key

    <Directory ${SRV_DIR}>
        Options Indexes MultiViews
        AllowOverride None
        Require all granted
    </Directory>
    ErrorLog ${SRV_LOG}/error.log
    LogLevel warn
</VirtualHost>
EOF"
```

```bash
sudo rm -fr /etc/apache2/sites-enabled/000-default.conf
```

```bash
sudo a2ensite http_yomo.conf
sudo a2ensite https_yomo.conf
sudo a2enmod ssl
sudo systemctl restart apache2
```

### build the repo tool

```bash
bitbake yocto-repo-manager
bitbake yocto-repo-manager-native -c addto_recipe_sysroot
```

### Publish the rpm repositories

```bash
mkdir -p ${SRV_DIR}/yomo_repositories/testRepository
oe-run-native yocto-repo-manager-native repo-manager -i ./tmp/deploy/rpm/ -o ${SRV_DIR}/yomo_repositories -r testRepository -v
```

### Build the sdk bootstrap

```bash
bitbake sdk-bootstrap
```

Publish your SDK boot strap

```bash
mkdir -p ${SRV_DIR}/yomo_repositories/testRepository
cp tmp/deploy/sdk/x86_64-sdk-bootstrap-*.sh ${SRV_DIR}/yomo_repositories/testRepository
```

###

### Init your SDK

```bash
```

### Update your SDK

```bash

```

### Use your SDK

```bash

```
