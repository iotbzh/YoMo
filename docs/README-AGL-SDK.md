# AGL SDK 

## build AGL-SDK

Add "meta-agl-AGLsdk" to your 

We need somme tiny fix on the SDK RPM

```
BBLAYERS =+ " {$AGL-SDK-managed}/meta-agl-AGLsdk"
```

Build SDK repo

```bash
bitbake agl-demo-platform-crosssdk
```

## Build repo

```bash
{$AGL-SDK-managed}/Update-SDK-repo.py -i ${WORK_DIR}/build_m3ulcb/tmp/deploy/rpm/ -o ${REPO_DIR} -r m3
```
