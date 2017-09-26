#Publish RPM repositories from yocto build

## Build RPM SDK

## Copy RPM and generate repositories

You need to install the tools "createrepo"

```bash
./AGL-SDK-managed/Update-SDK-repo.py -i ./workspace_agl_master/build_${machine}/tmp/deploy/rpm/ -o ./repo/repo/ -r ${machine}
```

## Http server conf

### apache template


Using port: 8000
Using directory: /home/devel/mirror/repo/
Apache version: 2.4.10

```bash
 cat /etc/apache2/sites-available/AGL-repo.conf 
<VirtualHost *:8000>

    ServerAdmin XXXX@iot.bzh
    DocumentRoot /home/devel/mirror/repo/

    <Directory "/home/devel/mirror/repo/">
        Options All
        AllowOverride All
        Require all granted
        Options Indexes FollowSymLinks
        DirectoryIndex disabled
        Options Indexes FollowSymLinks
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>
```

