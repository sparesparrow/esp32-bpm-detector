#!/bin/bash

# Generate Android launcher icons for BPM detector app
# Creates a heartbeat waveform style icon

# Colors
BG_COLOR="#1976D2"      # Blue background
WAVE_COLOR="#FFFFFF"    # White waveform
SHADOW_COLOR="#0D47A1"  # Darker blue shadow

# Icon sizes for each density
declare -A sizes=(
    ["mdpi"]="48"
    ["hdpi"]="72"
    ["xhdpi"]="96"
    ["xxhdpi"]="144"
    ["xxxhdpi"]="192"
)

echo "Generating Android launcher icons..."

for density in "${!sizes[@]}"; do
    size=${sizes[$density]}
    dir="android-app/app/src/main/res/mipmap-${density}"

    echo "Creating ${density} icons (${size}x${size})..."

    # Create square icon with heartbeat waveform
    convert -size ${size}x${size} xc:"$BG_COLOR" \
        -fill "$WAVE_COLOR" \
        -stroke "$SHADOW_COLOR" \
        -strokewidth 1 \
        -draw "bezier 8,${size}/2 ${size}/4,${size}/4 ${size}/2,${size}/2 ${size}*3/4,${size}*3/4" \
        -draw "bezier ${size}*3/4,${size}*3/4 ${size}*7/8,${size}/4 ${size},${size}/2 ${size}*15/16,${size}/2" \
        -gravity center \
        -pointsize $((size/6)) \
        -fill "$WAVE_COLOR" \
        -annotate +0+$((${size}*2/5)) "BPM" \
        "${dir}/ic_launcher.png"

    # Create round icon (Android adaptive icon background)
    convert -size ${size}x${size} xc:"$BG_COLOR" \
        -fill "$WAVE_COLOR" \
        -stroke "$SHADOW_COLOR" \
        -strokewidth 1 \
        -draw "bezier 8,${size}/2 ${size}/4,${size}/4 ${size}/2,${size}/2 ${size}*3/4,${size}*3/4" \
        -draw "bezier ${size}*3/4,${size}*3/4 ${size}*7/8,${size}/4 ${size},${size}/2 ${size}*15/16,${size}/2" \
        -gravity center \
        -pointsize $((size/6)) \
        -fill "$WAVE_COLOR" \
        -annotate +0+$((${size}*2/5)) "BPM" \
        "${dir}/ic_launcher_round.png"

    echo "✓ Created ${dir}/ic_launcher.png"
    echo "✓ Created ${dir}/ic_launcher_round.png"
done

echo "Icon generation complete!"
echo ""
echo "Generated icons:"
ls -la android-app/app/src/main/res/mipmap-*/ic_launcher*