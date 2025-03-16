#!/usr/bin/bash
# This script processes audio files metadata and exports it to a specified output file.

# Check if AUDIO_DIR is provided as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <AUDIO_DIR> [OUTPUT_FILENAME]"
    exit 1
fi

AUDIO_DIR="$1"
OUTPUT_FILENAME="${2:-songs.csv}"
OUTPUT="${TONITUNES_HOME}/songs/${OUTPUT_FILENAME}"
sep=","
q=\"\"

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT")"


# Write CSV header only if the output file does not exist
if [ ! -f "$OUTPUT" ]; then
    echo "title"$sep"artist"$sep"album"$sep"filename"$sep"duration" >"$OUTPUT"
fi

# Function to check if line already exists in output file
line_exists() {
    local line="$1"
    grep -Fxq "$line" "$OUTPUT"
}

# Find and process audio files
find "$AUDIO_DIR" -type f -name "*.mp3" -print0 | while IFS= read -r -d '' file; do
    metadata=$(mediainfo --Inform="General;$q%Title%$q$sep$q%Performer%$q$sep$q%Album%$q$sep$q$AUDIO_DIR/%FileNameExtension%$q$sep%Duration%" "$file" | sed 's/""//g')
    if ! line_exists "$metadata"; then
        echo "$metadata" >> "$OUTPUT"
    fi
done

echo "Audio files metadata has been successfully exported to $OUTPUT"
