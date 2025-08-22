import feedparser
import requests
from bs4 import BeautifulSoup
import ollama
from gtts import gTTS
from dotenv import load_dotenv
import os
from pexels_api import API
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
api = API(PEXELS_API_KEY)

# Gets latest news headlines
def get_headlines():
    url = "http://feeds.bbci.co.uk/news/technology/rss.xml"
    feed = feedparser.parse(url)

    # Gets latest headlines
    for entry in feed.entries[:5]:
        print("Title:", entry.title)
        print("Link:", entry.link)
        print("Published:", entry.published)
        print()

url = 'https://www.bbc.co.uk/news/articles/c24zdel5j18o?at_medium=RSS&at_campaign=rss'

article = """I love tv shoes especially like spongebob because it is hilarious"""

# Gets article content from URL
def get_article():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(url, headers=headers)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find(id="main-heading").find("span")
    print(title)
    article = soup.find_all("article")
    for a in article:
        print(a.text)

# Generates a script using given article
def generate_script(article):
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
    print(response)

# generate_script(article)


def voiceover():
    script = "hello this is a quick test of how well this works. i hope it works well."
    # Convert to speech
    tts = gTTS(text=script, lang='en')

    # Save as mp3
    tts.save("voiceover.mp3")

    print("Audio saved as voiceover.mp3")

clips = []
def videos():
    messages = [{"role": "system", "content": "You  are needed to search for stock videos relevant to the text. Give up to five words to search for a stock videos. only state these five words, nothing else"}]
    messages.append({"role": "user", "content": "The text to generate the five words for is: " + article})
    response = ollama.chat(model='gemma3', messages=messages)
    response = response["message"]["content"]
    print(response)

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

def edit_video():
    clips = ["0.mp4", "1.mp4", "2.mp4"]

    subtitles = [
        (0, 5, "Welcome to the video!"),
        (5, 10, "Here we talk about technology."),
        (10, 15, "Thanks for watching!")
    ]

    processed_clips = []
    # for clip in clips:
    #     video = VideoFileClip(clip)
    #     video = video.subclip(0, 4)
    #     video = video.resize(height=1920).crop(width=1080, height=1920,  x_center=video.w/2, y_center=video.h/2)

    #     print(os.getcwd())
    #     video.write_videofile("b" + clip)
    #     processed_clips.append(video)

    subtitles = [
        (0, 5, "Welcome to the video!"),
        (5, 10, "Here we talk about technology."),
        (10, 15, "Thanks for watching!")
    ]
    processed_clips = []
    for i, c in enumerate(clips):
        video = VideoFileClip(c)
        video = video.subclip(0, 5)
    
        # Resize to height 1920 while keeping aspect ratio
        video = video.resize(height=1920)

        # Crop width to 1080 (centered)
        if video.w > 1080:
            video = video.crop(width=1080, height=1920, x_center=video.w / 2, y_center=video.h / 2)
    
        processed_clips.append(video)

    final = concatenate_videoclips(processed_clips, method="compose")
    final.write_videofile("final.mp4")
edit_video()
