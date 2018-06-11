inherit yomo-toolchain-scripts

create_sdk_files_append() {
	yomo_toolchain_create_sdk_env_script ${SDK_OUTPUT}/${SDKPATH}/yomo-environment-setup-${REAL_MULTIMACH_TARGET_SYS}
}
