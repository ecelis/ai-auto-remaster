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

- video.mp4: The modernized video file.
- audio.mp3: Isolated audio.
- subtitles.srt: English subtitles synchronized to the video.

🎨 The AI Remastering Guide (Post-Processing)

These scripts prepare your files. To achieve "Pro Quality," follow these steps with the output files:

Phase 1: Video Upscaling

First, you need to turn your video into a sequence of individual image files.

Create a folder for your images first (e.g., `original_frames`) to keep things organized.

Run this command in your terminal:

```bash
mkdir -vp input_files/processed/original_frames
ffmpeg -i input_files/processed/video.mp4 -q:v 2 input_files/processed/original_frames/frame_%04d.jpg
```

-i input_movie.mp4: Your source video.

-q:v 2: Sets the quality for JPEG (1 is highest, 31 is lowest). You can also use .png for lossless quality, but the files will be much larger.

frame\_%04d.jpg: Creates filenames like frame_0001.jpg, frame_0002.jpg. The %04d ensures they are numbered correctly with padding zeros, which is crucial for re-stitching later.

    TODO

Once you have your folder of upscaled images, use FFmpeg to combine them back into a video file.

```bash
ffmpeg -framerate 30 -pattern_type glob -i 'input_files/processed/upscaled_frames_PalmillasTierrasAridas/frame_*.jpg' -c:v libx264 -pix_fmt yuv420p upscaled_movie_silent.mp4
```

```bash
ffmpeg -i upscaled_movie_silent.mp4 -vf "deflicker=mode=pm:size=10,minterpolate=mi_mode=mci:mc_mode=aobmc:me_mode=bidir:mb_size=16" -c:v libx264 -crf 18 smooth_output.mp4
```

-framerate 30: Important: Replace 30 with the framerate of your original video. If you don't know it, check the original file first.

-i ...: The pattern of your upscaled images. If the upscaler changed the extension to PNG, change .jpg to .png here.

-c:v libx264: Encodes the video using the standard H.264 codec (widely compatible).

-pix_fmt yuv420p: Ensures the video works on all media players (QuickTime, Windows Media Player, etc.).

Get a sample to compare.

```bash
ffmpeg -i input.asf -vf "trim=start_frame=1130:end_frame=1370,setpts=PTS-STARTPTS" -an -c:v libx264 -crf 0 output_snippet.mp4
```

trim=start_frame=1130:end_frame=1370: Keeps frames starting at 1130 and stops before 1370 (so it includes 1369).

setpts=PTS-STARTPTS: Resets the timestamp to 0. Without this, your player might show a black screen for the first ~40 seconds until it reaches the cut point.

-an: Removes audio.

-crf 0: Sets the encoding to Lossless. This is crucial for your upscaling workflow so you don't introduce new compression artifacts before the AI sees it.

```bash
ffmpeg -i input.asf -vf "trim=start_frame=1130:end_frame=1370,setpts=PTS-STARTPTS" -q:v 2 frames/frame_%04d.jpg
```

This will create images numbered frame_0001.jpg, frame_0002.jpg, etc., but they will actually be the content of frames 1130–1369 from the original video.

Note: If you want the filenames to match the original frame numbers (e.g., frame_1130.jpg), it is much harder to do in FFmpeg directly. It is usually easier to use the command above and then treat 0001 as your "start" for that batch.

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

## NOtes

Run time

```

real    3m43.415s
user    14m28.106s
sys     0m13.158s

real    41m9.262s
user    0m24.780s
sys     0m1.592s
```

Video-to-Video (Vid2Vid): Models like Stable Video Diffusion (SVD) or AnimateDiff take a video as input, not just images. They look at 10-20 frames at once to ensure the nose doesn't change shape.

Specialized Tools: Topaz Video AI or TensorPix use "Optical Flow" to track pixels over time. They don't "hallucinate" new details as much as "enhance" existing ones, resulting in 100% stable video.
