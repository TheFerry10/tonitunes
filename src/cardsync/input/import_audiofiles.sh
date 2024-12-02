#!/usr/bin/bash
AUDIO_DIR="/mnt/tonibox-media/audio/Audials Music"
output="out.csv"
sep=","
q=\"\"
echo "title"$sep"artist"$sep"album"$sep"filename"$sep"duration" >"$output"
find "$AUDIO_DIR" -type f -name "*.mp3" -print0 |
xargs -0 -I {} mediainfo --Inform="General;$q%Title%$q$sep$q%Performer%$q$sep$q%Album%$q$sep$q%FileNameExtension%$q$sep%Duration%" {} |
sed 's/""//g' >> "$output"

