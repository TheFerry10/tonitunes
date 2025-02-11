# This script processes audio files metadata and exports it to a specified output file.
#!/usr/bin/bash
AUDIO_DIR="/home/malte/Music/Audials/Music"
OUTPUT="resources/songs.csv"
sep=","
q=\"\"
echo "title"$sep"artist"$sep"album"$sep"filename"$sep"duration" >"$OUTPUT"
find "$AUDIO_DIR" -type f -name "*.mp3" -print0 |
xargs -0 -I {} mediainfo --Inform="General;$q%Title%$q$sep$q%Performer%$q$sep$q%Album%$q$sep$q%FileNameExtension%$q$sep%Duration%" {} |
sed 's/""//g' >> "$OUTPUT"
echo "Audio files metadata has been successfully exported to $OUTPUT"
