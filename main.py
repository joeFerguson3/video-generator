import feedparser
import requests
from bs4 import BeautifulSoup
import ollama
from gtts import gTTS
from dotenv import load_dotenv
import os
from pexels_api import API
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip

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
    print("Generating script \n")
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
    print("Creating voiceover \n")
    # Convert to speech
    tts = gTTS(text=script, lang='en')

    # Save as mp3
    tts.save("voiceover.mp3")
    videos(script)

clips = []
def videos(script):
    print("Finding relevant video clips...\n")
    messages = [{"role": "system", "content": "You  are needed to search for stock videos relevant to the text. Give 3 video searches to make, seperate each search with with a comma only. Include no other text in your response"}]
    messages.append({"role": "user", "content": "The text to generate the search for videos for is: " + script})
    response = ollama.chat(model='gemma3', messages=messages)
    response = response["message"]["content"]
    print("searching for " + response)

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": response, "per_page": 3, "page": 1}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    for i, video in enumerate(data["videos"]):
        # Get the highest quality video file
        video_file = video["video_files"][-1]
        video_url = video_file["link"]
        filename = f"{i}.mp4"
        clips.append(filename)

        r = requests.get(video_url)
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"Downloaded {filename}")

    edit_video()

def edit_video():
    print("Editing video... \n")
    clips = ["0.mp4", "1.mp4", "2.mp4"]

    subtitles = [
        (0, 5, "Welcome to the video!"),
        (5, 10, "Here we talk about technology."),
        (10, 15, "Thanks for watching!")
    ]

    processed_clips = []
    for i, c in enumerate(clips):
        video = VideoFileClip(c)
        video = video.subclip(0, 10)
    
        # Resize to height 1920 while keeping aspect ratio
        video = video.resize(height=1920)

        # Crop width to 1080 (centered)
        if video.w > 1080:
            video = video.crop(width=1080, height=1920, x_center=video.w / 2, y_center=video.h / 2)
    
        processed_clips.append(video)

    final = concatenate_videoclips(processed_clips, method="compose")
    audio = AudioFileClip("voiceover.mp3")
    final = final.set_audio(audio)
    final.write_videofile("final.mp4")

get_headlines()
