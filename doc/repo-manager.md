# repository manager

## Build

Add meta-yomo  to your conf/bblayers.conf

```bash
BBLAYERS += "${WORKDIR}/YoMo/meta-yomo"
```

## Build yocto-repo-manager

```bash
bitbake yocto-repo-manager
bitbake yocto-repo-manager-native -c addto_recipe_sysroot
```

## Test

```bash
oe-run-native yocto-repo-manager-native repo-manager -i ./tmp/deploy/rpm/ -o ~/public_html/ -r testRepository -v
```