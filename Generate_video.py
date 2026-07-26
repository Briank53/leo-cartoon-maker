import json
import os
from gtts import gTTS
from moviepy.editor import *
from PIL import Image
import requests
import io

# 1. Load story
with open("story.json", "r", encoding="utf-8") as f:
    story = json.load(f)

os.makedirs("output", exist_ok=True)
os.makedirs("output/temp", exist_ok=True)

clips = []

print("Starting to generate scenes...")

for i, scene in enumerate(story["scenes"]):
    print(f"Generating scene {i+1}: {scene['text']}")
    
    # 2. Generate voiceover
    tts = gTTS(text=scene["text"], lang="en", slow=False)
    audio_path = f"output/temp/scene_{i}.mp3"
    tts.save(audio_path)
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # 3. Generate cartoon image using free AI API
    # This uses Pollinations.ai - free, no key needed
    prompt = scene["image_prompt"] + ", cartoon style, 4k, vibrant colors"
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    
    response = requests.get(url)
    img = Image.open(io.BytesIO(response.content))
    img_path = f"output/temp/scene_{i}.png"
    img.save(img_path)
    
    # 4. Make image into video clip with zoom effect
    img_clip = ImageClip(img_path, duration=duration)
    img_clip = img_clip.resize(lambda t: 1 + 0.05*t) # slow zoom in
    img_clip = img_clip.set_position("center")
    
    # Combine image + audio
    video_clip = img_clip.set_audio(audio)
    clips.append(video_clip)

# 5. Stitch all scenes together
print("Stitching video...")
final_video = concatenate_videoclips(clips, method="compose")

# Add background music if you have one
# music = AudioFileClip("music.mp3").volumex(0.2)
# final_video = final_video.set_audio(CompositeAudioClip([final_video.audio, music]))

output_path = f"output/{story['title']}.mp4"
final_video.write_videofile(output_path, fps=24, codec="libx264")

print(f"Done! Video saved at {output_path}")
