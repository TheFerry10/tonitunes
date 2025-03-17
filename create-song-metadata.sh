#!/usr/bin/bash
# This script processes audio files metadata and exports it to a specified output file.
#
# Usage:
#   ./create-song-metadata.sh <AUDIO_DIR> [OUTPUT_FILENAME]
#
# Arguments:
#   AUDIO_DIR        The directory containing audio files to process.
#   OUTPUT_FILENAME  (Optional) The name of the output CSV file. Defaults to 'songs.csv'.
#
# Environment Variables:
#   TONITUNES_HOME   The base directory where the output file will be stored.
#
# Description:
#   - The script checks if the AUDIO_DIR argument is provided. If not, it displays usage information and exits.
#   - It sets the AUDIO_DIR and OUTPUT_FILENAME variables based on the provided arguments.
#   - The output file path is constructed using the TONITUNES_HOME environment variable and the OUTPUT_FILENAME.
#   - The script creates the output directory if it does not exist.
#   - If the output file does not exist, it writes the CSV header to the file.
#   - The script defines a function 'line_exists' to check if a line already exists in the output file.
#   - It finds and processes all .mp3 files in the AUDIO_DIR, extracting metadata using 'mediainfo'.
#   - If the metadata line does not already exist in the output file, it appends the metadata to the file.
#   - Finally, it prints a success message indicating the metadata has been exported.

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
