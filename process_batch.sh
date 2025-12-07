#!/bin/bash

# process_batch.sh
# Usage: ./process_batch.sh /path/to/files

INPUT_DIR="$1"
OUTPUT_DIR="$INPUT_DIR/processed"

# Check if input directory is provided
if [ -z "$INPUT_DIR" ]; then
  echo "Error: Please provide a directory path."
  echo "Usage: ./process_batch.sh ./my_old_videos"
  exit 1
fi

# Activate Python environment for Whisper
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
else
  echo "Error: Virtual environment not found. Run ./setup_env.sh first."
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "--- Starting Batch Process on $INPUT_DIR ---"

# Loop through likely extensions
for file in "$INPUT_DIR"/*.{asx,asf,wmv}; do
  [ -e "$file" ] || continue # Skip if no files found

  filename=$(basename -- "$file")
  basename="${filename%.*}"

  echo "=========================================="
  echo "Processing: $filename"
  echo "=========================================="

  # 1. CONVERT VIDEO
  # -vf yadif: De-interlace (crucial for old TV recordings)
  # -crf 18: High quality visual preservation
  # -c:a aac: Standard audio
  echo "Step 1: Converting video to MP4..."
  ffmpeg -y -i "$file" \
    -c:v libx264 -preset slow -crf 18 -vf yadif \
    -c:a aac -b:a 192k \
    "$OUTPUT_DIR/${basename}.mp4" -hide_banner -loglevel error

  if [ $? -eq 0 ]; then
    echo "✅ Video conversion successful."
  else
    echo "❌ Video conversion failed. Check input file."
    continue
  fi

  # 2. EXTRACT AUDIO (For transcription)
  echo "Step 2: Extracting audio for transcription..."
  ffmpeg -y -i "$OUTPUT_DIR/${basename}.mp4" \
    -vn -acodec libmp3lame -q:a 2 \
    "$OUTPUT_DIR/${basename}.mp3" -hide_banner -loglevel error

  # 3. TRANSCRIBE & TRANSLATE (Whisper)
  # --task translate: Translates ANY language input directly to English text
  # --model medium: Good balance. Use 'large' if you have a GPU.
  echo "Step 3: Transcribing and Translating to English..."
  whisper "$OUTPUT_DIR/${basename}.mp3" --model medium --task translate --output_format srt --output_dir "$OUTPUT_DIR"

  # 4. EXTRACT FRAMES FOR UPSCALE
  echo "Step 4: Extracting frames for AI upscaling..."
  mkdir -p "$OUTPUT_DIR/original_frames_${basename}"
  ffmpeg -i "$OUTPUT_DIR/${basename}.mp4" -q:v 2 "$OUTPUT_DIR/original_frames_${basename}/frame_%04d.jpg" -hide_banner -loglevel error

  echo "✅ Finished processing $basename"
done




echo "--- All tasks complete! Check the '$OUTPUT_DIR' folder. ---"
