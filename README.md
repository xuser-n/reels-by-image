# reels-by-image
image to video by using gemini api key
# 🎬 Reels by Image

Reels by Image is a Streamlit web app that generates **12-second AI marketing reels** from an image with **Gemini TTS voiceover** and **background music**, plus **SEO-friendly YouTube title & description**.

## Features

- 12-second reel (4s black intro + 8s video)
- Background music from `audio.mp3`
- Gemini TTS voiceover starting at 4 seconds
- SEO-friendly title & description (1 option, trendy/classic)
- Copy buttons for title & description
- Download final video directly from the page
- UI language: English / Hinglish

## Requirements

- Python 3.10+
- Streamlit
- MoviePy 1.0.3
- google-genai
- python-dotenv

## Installation

```bash
git clone https://github.com/<your-username>/reels-by-image.git
cd reels-by-image
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt

