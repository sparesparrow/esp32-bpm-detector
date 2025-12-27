# GDB initialization for ESP32-S3 JTAG debugging

# Connect to OpenOCD
target remote :3333

# Set architecture  
set architecture riscv:rv32

# Load symbols
file .pio/build/esp32-s3/firmware.elf

# Enable pretty printing
set print pretty on

# Define helper function to dump logs
define dumplogs
    set $i = 0
    set $count = logCount
    if $count > 100
        set $count = 100
    end
    while $i < $count
        if logBuffer[$i].valid
            printf "%s\n", logBuffer[$i].data
        end
        set $i = $i + 1
    end
    # Write to file
    set logging file .cursor/debug.log
    set logging on
    dumplogs
    set logging off
end

# Set breakpoint at main
break main
break setup
break loop

# Continue execution
continue
