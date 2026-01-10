script_folder="/home/sparrow/projects/embedded-systems/esp32-bpm-detector"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
for v in ESP32_BPM_DETECTOR_VERSION ESP32_TARGET_BOARD PYTHONPATH SPARETOOLS_MCP_CORE_VERSION
do
    is_defined="true"
    value=$(printenv $v) || is_defined="" || true
    if [ -n "$value" ] || [ -n "$is_defined" ]
    then
        echo export "$v='$value'" >> "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
    else
        echo unset $v >> "$script_folder/deactivate_conanrunenv-release-x86_64.sh"
    fi
done


export ESP32_BPM_DETECTOR_VERSION="0.1.0"
export ESP32_TARGET_BOARD="esp32s3"
export PYTHONPATH="/home/sparrow/.conan2/p/b/spare0025b88ce307f/p/lib/python:$PYTHONPATH"
export SPARETOOLS_MCP_CORE_VERSION="1.0.0"