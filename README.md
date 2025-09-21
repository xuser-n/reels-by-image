# reels-by-image
image to video by using gemini api key
# 🎬 Reels by Image

Reels by Image is a Streamlit web app that generates **12-second AI marketing reels** from an image with **Gemini TTS voiceover** and **background music**, plus **SEO-friendly YouTube title & description**.
**it uses mainly gemini api key to generate vedio it uses veo-3/veo-2
## Folder Structure
reels-by-image/
│
├── app.py                 # Your Streamlit app (full 12s reel code)
├── requirements.txt       # Dependencies(create yourself)
├── README.md              # Project description & instructions
├── .env                   # Your GEMINI_API_KEY (create your file and upload api key here)
├── audio.mp3              # Background music file
└── .gitignore             # To ignore .env and other sensitive files
|__vedio.mp4               # to store generate vedio here.

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
```

GEMINI_API_KEY=your_gemini_api_key_here

Place your audio.mp3 file in the root folder.(add background sound you want to add )

##Run the App
     streamlit run app.py

     



