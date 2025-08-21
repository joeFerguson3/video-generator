import feedparser
import requests
from bs4 import BeautifulSoup
import ollama
from gtts import gTTS

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

article = """An investigation has been launched into the death of a French streamer known for extreme challenges.

Raphaël Graven, also known as Jean Pormanove, was found dead at a residence in Contes, a village north of Nice, prosecutors said.

The 46-year-old had been subject to bouts of violence and sleep deprivation during streams, and died in his sleep during a live broadcast, local media reported.

Confirming a judicial investigation was under way, French government minister Clara Chappaz described Mr Graven's death and violence he endured as an "absolute horror", adding he had been "humiliated" for months.

Top tips to help people game online safely

What is the streaming platform Kick?

Meta investigated over AI having 'sensual' chats with children

A spokesperson for Kick - a live-streaming platform similar to Twitch, on which users can broadcast content and interact with other users in real-time - told the BBC the company was "urgently reviewing" circumstances around the streamer's death.

"We are deeply saddened by the loss of Jean Pormanove and extend our condolences to his family, friends and community," they said.

The platform's community guidelines were "designed to protect creators" and Kick was "committed to upholding these standards across our platform", the spokesperson added.

Chappaz, the minister delegate for artificial intelligence and digital technologies, said she had referred the issue to Arcom, the French media regulator, and Pharos, a French system used to report online content.

Sarah El Haïry, France's High Commissioner for Children, described the death as "horrifying".

"Platforms have an immense responsibility in regulating online content so that our children are not exposed to violent content. I call on parents to be extremely vigilant", she wrote on X, external.

The prosecutor's office confirmed it had opened an investigation into the cause of death and ordered an autopsy, the AFP news agency reports.

Jean Pormanove had more than one million followers across his various social media platforms and had built a strong community on Kick.

One of his co-creators Owen Cenazandotti, known as Naruto, announced Jean Pormanove's death on Instagram, external and paid tribute to his "brother, sidekick, partner," and asked people to "respect" his memory and not to share videos of his "last breath" online."""

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

voiceover()