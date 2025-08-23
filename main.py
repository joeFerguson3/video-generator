import feedparser
import requests
from bs4 import BeautifulSoup
import ollama
from gtts import gTTS
from dotenv import load_dotenv
import os
from pexels_api import API
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip
from mutagen.mp3 import MP3
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
api = API(PEXELS_API_KEY)

# Gets latest news headlines
def get_headlines():
    print("Finding headlines.. \n")
    url = "http://feeds.bbci.co.uk/news/technology/rss.xml"
    feed = feedparser.parse(url)

    # Gets latest headlines
    for entry in feed.entries[:1]:
        print("Title:", entry.title)
        print("Link:", entry.link)
        print("Published:", entry.published)
        get_article(entry.link)

# Gets article content from URL
def get_article(url):
    print("Getting article... \n")
    text = ""
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
 
    article = soup.find_all("article")
    for a in article:
        text += a.text
    generate_script(text)

# Generates a script using given article
def generate_script(article):
    print("Generating script... \n")
    messages = [{"role": "system", "content": """ You are a short-form video scriptwriter. 
Generate an engaging narration for a ~30-second video about the topic provided. 
Output ONLY the text to be spoken as a voiceover, no music, images etc. 
Keep sentences short, punchy, and natural for spoken language.
                 The reader has no prior context so they must understand what the video is talking about
                 Exagerate (but dont make up anything untrue) tomake the video more engaging
"""}]
    messages.append({"role": "user", "content": "The article to generate a video script for is: " + article})

    # Generates ai response
    response = ollama.chat(model='gemma3', messages=messages)
    print(response['message']['content'])
    voiceover(response['message']['content'])

# generate_script(article)


def voiceover(script):
    print("Creating voiceover... \n")
    parts = script.split("**")
    print(parts)
    for i in range(2, len(parts), 2):
        # Convert to speech
        tts = gTTS(text=parts[i], lang='en')
        # Save as mp3
        tts.save(str(int((i / 2) - 1)) + ".mp3")
 
        find_video(parts[i], int((i / 2) - 1))   
    edit_video(int((len(parts) - 1) / 2), parts)

from moviepy.editor import CompositeVideoClip, TextClip
from moviepy.video.tools.subtitles import SubtitlesClip

# Adds subtitles to video
def add_subtitles(video, text, duration):
    font = ImageFont.truetype(r"c:\WINDOWS\Fonts\ARIALBD.TTF", 70)

    def draw_subtitle(frame):
        img = Image.fromarray(frame)
        draw = ImageDraw.Draw(img)
        w, h = img.size

        max_chars = w // (font.size // 2)
        wrapped = textwrap.fill(text, width=max_chars)

        # Get text size using textbbox
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=10)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        position = ((w - text_w)//2, h - text_h - 300)
        draw.multiline_text(position, wrapped, font=font, fill="white", stroke_width=5, stroke_fill="black", spacing=10)
        return np.array(img)

    # Apply the subtitle to all frames for the given duration
    return video.subclip(0, duration).fl_image(draw_subtitle)


clips = []
def find_video(script, number):
    print("Finding relevant video clips...\n")
    messages = [{"role": "system", "content": "You  are needed to search for stock videos relevant to the text. Give 3 video searches to make, seperate each search with with a comma only. Include no other text in your response"}]
    messages.append({"role": "user", "content": "The text to generate the search for videos for is: " + script})
    response = ollama.chat(model='gemma3', messages=messages)
    response = response["message"]["content"]
    print("searching for " + response)

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": response, "per_page": 1, "page": 1}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    for i, video in enumerate(data["videos"]):
        # Get the highest quality video file
        video_file = video["video_files"][-1]
        video_url = video_file["link"]
        filename = f"{number}.mp4"
        clips.append(filename)

        r = requests.get(video_url)
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"Downloaded {filename}")

def edit_video(clip_num, subtitles):
    print("Editing video... \n")

    processed_clips = []
    for i in range(0, clip_num - 1):
        video = VideoFileClip(str(i) + ".mp4")
        duration = MP3(str(i) + ".mp3").info.length
        video = video.subclip(0, duration)
       
        audio = AudioFileClip(str(i) + ".mp3")
        video = video.set_audio(audio)
        # Resize to height 1920 while keeping aspect ratio
        video = video.resize(height=1920)

        # Crop width to 1080 (centered)
        if video.w > 1080:
            video = video.crop(width=1080, height=1920, x_center=video.w / 2, y_center=video.h / 2)

        video = add_subtitles(video, subtitles[i], duration) #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! FIX
        processed_clips.append(video)

    final = concatenate_videoclips(processed_clips, method="compose")
    final.write_videofile("final.mp4")

edit_video(5, ["thisis sub", "asadfj as flkjfd asf safjlsfj asfk asfjasdf as;fjdaljf aslfjafj asdfljasl;fkja sdflkajsdf;l asjdf;asjkdf  aksjdf;lasjf", "asdf", "asdf", "asdf"])
