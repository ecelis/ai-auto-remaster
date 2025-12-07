import argparse
import io
import os
import time

from google import genai
from google.genai import types
from PIL import Image

# --- CONFIGURATION DEFAULTS ---
# "Nano Banana Pro" = gemini-2.0-pro-exp-02-05 (or current preview)
# "Nano Banana Flash" = gemini-2.5-flash-image
DEFAULT_MODEL = "gemini-2.5-flash-image"

# Creativity (0.0 to 1.0)
# Low (0.1) = Faithful restoration (Best for video to avoid jitter)
# High (0.7) = Hallucinating details (Good for single images, bad for video)
DEFAULT_CREATIVITY = 0.15

# The "Magic" Prompt
DEFAULT_SYSTEM_PROMPT = """
You are a professional film remastering AI.
Your task is to upscale the input image to high-fidelity 4K resolution.
1. DENOISE: Remove compression artifacts and JPEG noise.
2. SHARPEN: Restore skin texture and edge details naturally.
3. FAITHFUL: Do NOT change the person's identity, facial expression, or clothing details.
4. OUTPUT: Return only the high-resolution image.
"""


class UpscaleAgent:
    def __init__(
        self, api_key, model_name=DEFAULT_MODEL, creativity=DEFAULT_CREATIVITY
    ):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.config = types.GenerateContentConfig(
            temperature=creativity,
            response_modalities=["IMAGE"],
            system_instruction=DEFAULT_SYSTEM_PROMPT,
        )
        print(f"Loaded Agent: {model_name} | Creativity: {creativity}")

    def process_frame(self, image_path, output_path):
        if os.path.exists(output_path):
            print(f"Skipping (exists): {os.path.basename(image_path)}")
            return

        print(f"Processing: {os.path.basename(image_path)}...")

        try:
            img = Image.open(image_path)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[img, "Upscale this to 4K."],
                config=self.config,
            )

            for part in response.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    upscaled_image = Image.open(io.BytesIO(image_data))
                    upscaled_image.save(output_path)
                    print(f" -> Saved to {output_path}")
                    return True

            print(f" [!] No image returned for {image_path}")

        except Exception as e:
            print(f" [!] Error: {e}")
            if "429" in str(e):
                print("Rate limit hit. Pausing for 20s...")
                time.sleep(20)


def main():
    parser = argparse.ArgumentParser(description="AI Video Upscaler")
    parser.add_argument("--input", "-i", required=True, help="Input folder of frames")
    parser.add_argument("--output", "-o", required=True, help="Output folder")
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help="Model name (e.g., gemini-2.0-flash-exp)",
    )
    parser.add_argument(
        "--temp",
        "-t",
        type=float,
        default=DEFAULT_CREATIVITY,
        help="Creativity/Temperature (0.0 - 1.0)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY environment variable.")
        return

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    agent = UpscaleAgent(api_key, args.model, args.temp)

    files = sorted(
        [f for f in os.listdir(args.input) if f.lower().endswith((".jpg", ".png"))]
    )

    for filename in files:
        in_path = os.path.join(args.input, filename)
        out_path = os.path.join(args.output, filename)
        agent.process_frame(in_path, out_path)

        # Safety sleep to prevent rapid-fire rate limits on Pro models
        time.sleep(2)


if __name__ == "__main__":
    main()
