inherit AGL-toolchain-scripts

create_sdk_files_append() {
	AGL_toolchain_create_sdk_env_script ${SDK_OUTPUT}/${SDKPATH}/AGL-environment-setup-${REAL_MULTIMACH_TARGET_SYS}
}
