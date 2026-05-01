#!/bin/bash
SOURCE_DIR="$(pwd)"
OUT_DIR="$SOURCE_DIR/PRISM_VARIANTS"
TEMP_DIR="$SOURCE_DIR/chimera_tmp"
mkdir -p "$TEMP_DIR" "$OUT_DIR"
if ! command -v sox &> /dev/null; then
    pkg install sox ffmpeg -y
fi
rand_float() {
    awk -v min=$1 -v max=$2 'BEGIN{srand(); print min+rand()*(max-min)}'
}
rand_int() {
    echo $(( ( RANDOM % ($2 - $1 + 1) ) + $1 ))
}
find "$SOURCE_DIR" -maxdepth 1 -type f \( -name "*.mp3" -o -name "*.flac" -o -name "*.wav" -o -name "*.m4a" -o -name "*.opus" -o -name "*.mp4" \) -print0 | while IFS= read -r -d '' FILE_PATH; do
    FILENAME=$(basename "$FILE_PATH")
    NAME_ONLY="${FILENAME%.*}"
    SAFE_NAME=$(echo "$NAME_ONLY" | sed 's/[^a-zA-Z0-9._-]/_/g')
    SPEED_VAL=$(rand_float 0.88 1.12)
    PITCH_VAL=$(rand_int -400 200)
    MODE_RNG=$(rand_int 1 5)
    case $MODE_RNG in
        1) FX_CHAIN="phaser 0.6 0.8 2 0.4 0.5 -s equalizer 2500 1.0q -3 highpass 80"; TAG="NeonPiano" ;;
        2) FX_CHAIN="lowpass 4500 overdrive 2.5 equalizer 300 1.0q +2 bass +3"; TAG="LiquidSilk" ;;
        3) FX_CHAIN="bass +6 treble -4 compand 0.1,0.3 -60,-60,-30,-10,-20,-8 -6 -90 0.1"; TAG="DeepFuture" ;;
        4) FX_CHAIN="equalizer 1000 2.0q +3 equalizer 4000 1.0q -4 contrast 10"; TAG="CyberJazz" ;;
        5) FX_CHAIN="sinc -n 100 -5000 overdrive 1.2 bass +2"; TAG="VaporTape" ;;
    esac
    OUT_FILE="$OUT_DIR/${SAFE_NAME}_[${TAG}_S${SPEED_VAL}_P${PITCH_VAL}].flac"
    TEMP_WAV="$TEMP_DIR/t.wav"
    ffmpeg -y -hide_banner -loglevel error -i "$FILE_PATH" -vn -ac 2 -ar 48000 -f wav "$TEMP_WAV"
    if [ -f "$TEMP_WAV" ]; then
        sox "$TEMP_WAV" -t flac -b 24 "$OUT_FILE" vol 0.7 speed "$SPEED_VAL" pitch "$PITCH_VAL" rate -v -s -I 96000 $FX_CHAIN compand 0.01,0.1 6:-70,-60,-20 -5 -90 0.1 norm -1.0 2>/dev/null
        if [ -s "$OUT_FILE" ]; then
            echo "[SIGNAL] $FILENAME -> $TAG"
        fi
    fi
    rm -f "$TEMP_WAV"
done
rm -rf "$TEMP_DIR"