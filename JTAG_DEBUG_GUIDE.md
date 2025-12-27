# JTAG Debugging Guide for ESP32-S3

## Overview
This project uses JTAG debugging via the ESP32-S3's built-in USB JTAG interface (ID 303a:1001) instead of Serial output.

## Hardware Setup
- ESP32-S3 DevKit with built-in USB JTAG
- USB connection to host computer
- Verify connection: `lsusb | grep "303a:1001"`

## Software Setup

### 1. Install OpenOCD (if not already installed)
```bash
sudo apt-get install openocd
```

### 2. Start OpenOCD
```bash
./start_jtag_debug.sh
```

### 3. Connect GDB
In a new terminal:
```bash
xtensa-esp32s3-elf-gdb -x gdbinit .pio/build/esp32-s3/firmware.elf
```

Or if using PlatformIO's toolchain:
```bash
~/.platformio/packages/toolchain-xtensa-esp32s3/bin/xtensa-esp32s3-elf-gdb -x gdbinit .pio/build/esp32-s3/firmware.elf
```

## Extracting Debug Logs

### Method 1: Using GDB `dumplogs` command
Once connected to GDB:
```
(gdb) dumplogs
```
This will extract all logs from the memory buffer and write them to `.cursor/debug.log`

### Method 2: Manual inspection in GDB
```
(gdb) print logCount
(gdb) print logBuffer[0].data
(gdb) print logBuffer[1].data
# ... etc
```

### Method 3: Memory dump via OpenOCD telnet
```bash
telnet localhost 4444
> mdw 0x3FC80000 100  # Dump memory (adjust address based on your build)
```

## Log Buffer Structure

The code uses a circular buffer in DRAM:
- `logBuffer[]`: Array of LogEntry structures
- `logWriteIndex`: Current write position
- `logCount`: Number of valid log entries
- Each entry contains: data (256 bytes), timestamp, valid flag

## Debugging Workflow

1. **Start OpenOCD**: `./start_jtag_debug.sh`
2. **Connect GDB**: Use the command above
3. **Set breakpoints**: Already set in `gdbinit` (setup, loop)
4. **Run program**: `continue` in GDB
5. **Extract logs**: Use `dumplogs` command or inspect memory
6. **Analyze logs**: Check `.cursor/debug.log`

## Troubleshooting

### OpenOCD fails to start
- Check USB connection: `lsusb | grep 303a`
- Check permissions: May need to add user to `dialout` group
- Try different USB port

### GDB can't connect
- Ensure OpenOCD is running on port 3333
- Check `openocd.log` for errors

### No logs in buffer
- Verify program is running (check breakpoints)
- Check `logCount` variable in GDB
- Ensure code is executing (step through with GDB)


