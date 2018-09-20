# Repository manager

## build the repo tool

```bash
bitbake yocto-repo-manager
bitbake yocto-repo-manager-native -c addto_recipe_sysroot
```

## Publish in rpm repositories

Publish the rpm:

```bash
export ARCH="h3ulcb"
export PUBDIR="yomo_repositories/${ARCH}" #add distro, etc.
mkdir -p ${SRV_DIR}/${PUBDIR}
oe-run-native yocto-repo-manager-native repo-manager -i ./tmp/deploy/rpm/ -o ${SRV_DIR}/${PUBDIR} -v
```