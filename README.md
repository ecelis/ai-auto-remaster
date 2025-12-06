# Legacy Media Restorer & Translator

A Linux toolkit to rescue, convert, and translate old video formats (WMA, ASF, ASX) into modern standards, preparing them for AI Remastering.

## 🚀 What this does

1. **Fixes Formats:** Renames deceptively named `.asx` files to `.asf`.
2. **Converts:** Uses `ffmpeg` to convert legacy containers to high-quality MP4 (H.264) and cleans interlacing artifacts.
3. **Transcribes & Translates:** Uses OpenAI Whisper locally to extract audio, recognize speech (Spanish/Other), and generate **English** subtitles (`.srt`) automatically.

## 🛠 Prerequisites

You need a Fedora Workstation system.

## 📦 Installation

1. Clone this repository.
2. Make the scripts executable:

```bash
chmod +x setup_env.sh process_batch.sh
./setup_env.sh
```

▶️ Usage

Put all your old .wma, .asf, or .asx files into a folder (e.g., input_files/).

Run the script pointing to that folder:
Bash

```bash
./process_batch.sh ./input_files
```

Output: You will find a processed/ folder containing:

- video_clean.mp4: The modernized video file.
- audio_track.mp3: Isolated audio.
- subtitles.srt: English subtitles synchronized to the video.

🎨 The AI Remastering Guide (Post-Processing)

These scripts prepare your files. To achieve "Pro Quality," follow these steps with the output files:

Phase 1: Video Upscaling

First, you need to turn your video into a sequence of individual image files.

Create a folder for your images first (e.g., `original_frames`) to keep things organized.

Run this command in your terminal:

```bash
ffmpeg -i input_movie.mp4 -q:v 2 original_frames/frame_%04d.jpg
```

-i input_movie.mp4: Your source video.

-q:v 2: Sets the quality for JPEG (1 is highest, 31 is lowest). You can also use .png for lossless quality, but the files will be much larger.

frame\_%04d.jpg: Creates filenames like frame_0001.jpg, frame_0002.jpg. The %04d ensures they are numbered correctly with padding zeros, which is crucial for re-stitching later.

    TODO

Once you have your folder of upscaled images, use FFmpeg to combine them back into a video file.

```bash
ffmpeg -framerate 30 -i upscaled_frames/frame_%04d.jpg -c:v libx264 -pix_fmt yuv420p upscaled_movie_silent.mp4
```

-framerate 30: Important: Replace 30 with the framerate of your original video. If you don't know it, check the original file first.

-i ...: The pattern of your upscaled images. If the upscaler changed the extension to PNG, change .jpg to .png here.

-c:v libx264: Encodes the video using the standard H.264 codec (widely compatible).

-pix_fmt yuv420p: Ensures the video works on all media players (QuickTime, Windows Media Player, etc.).

Phase 2: Audio Restoration

    TODO

```bash
ffmpeg -i upscaled_movie_silent.mp4 -i input_movie.mp4 -map 0:v -map 1:a -c copy final_upscaled_movie.mp4
```

-map 0:v: Takes the video stream from the first input (your new upscaled video).

-map 1:a: Takes the audio stream from the second input (your original video).

-c copy: Copies the data without re-encoding, so you lose no quality and it finishes instantly.

Phase 3: Translation Polish (Optional)

Tool: Google Gemini Advanced.

    Action: If the automated English subtitles have nuances that feel robotic, upload the .srt file to Gemini and ask: "Review these subtitles for natural flow and idiomatic accuracy, keeping the timestamps exactly the same."

Phase 4: Final Assembly

Use a video editor (or ffmpeg) to combine the Upscaled Video, Enhanced Audio, and Subtitles into one final master file.
