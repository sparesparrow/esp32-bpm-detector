Deploy firmware to connected ESP32 devices using the unified-dev-tools MCP server.

1. Detect connected devices using `unified-deployment.detect_devices`
2. Select target device (ESP32, ESP32-S3, Arduino)
3. Build firmware with appropriate Conan profile
4. Deploy using `unified-deployment.deploy` with device-specific configuration
5. Monitor serial output for deployment status

Check device connection and serial ports before deployment. Use appropriate Conan profile for target device.

