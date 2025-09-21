import os
import tempfile
import time
import wave
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, ColorClip, concatenate_videoclips

# -------------------- Helpers --------------------
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

def generate_youtube_package(client, product_name, script, language="English"):
    prompt = f"""
You are a YouTube SEO & marketing expert.
Produce 1 trendy + classic style option containing:
  - SEO-friendly title (<=60 chars)
  - Short SEO-improved description (1-2 lines) with trending hashtags and a CTA.

Product: {product_name}
Script: {script}
Language: {language}

Return valid JSON only:
{{
  "titles": ["title1"],
  "descriptions": ["desc1"]
}}
    """
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        data = json.loads(response.text)
        title = data.get("titles", ["Default Title"])[0]
        desc = data.get("descriptions", ["Default Description"])[0]
        return title, desc
    except Exception:
        return f"{product_name} — Try Now", f"Check out {product_name}! {script} #mustwatch"

# -------------------- Sidebar --------------------
st.sidebar.header("⚙️ Settings")
ui_lang = st.sidebar.selectbox("🌍 UI Language", ["English", "Hinglish"])
language = st.sidebar.selectbox("🌍 Language", ["English", "Hindi", "Spanish", "French", "German"])
tone = st.sidebar.selectbox("✨ Tone", ["Professional", "Funny", "Emotional", "Trendy", "Luxury"])
reel_type = st.sidebar.selectbox("🎥 Reel Type", ["Product Promo", "Storytelling", "Tutorial", "Emotional Appeal"])

# -------------------- Main Inputs --------------------
product_name = st.text_input("📦 Product Name")
product_description = st.text_area("📝 Short Description (1–2 lines)")
uploaded_image = st.file_uploader("📸 Upload Product Image", type=["jpg", "jpeg", "png"])

# -------------------- Background audio --------------------
bg_audio_path = os.path.join("audio.mp3")
if not os.path.exists(bg_audio_path):
    st.error("⚠️ Background audio file (audio.mp3) not found!")
    st.stop()

# -------------------- Gemini Setup --------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ Gemini API key not found in .env")
    st.stop()
client = genai.Client(api_key=api_key)

# -------------------- Generate Process --------------------
if st.button("🚀 Generate Reel"):
    if not product_name or not product_description or not uploaded_image:
        st.warning("⚠️ Fill product name, description & upload image!")
    else:
        # ---- Step 1: Script (~8s one-liner) ----
        with st.spinner("✨ Generating script..."):
            resp = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"You are an ad copywriter. Write a catchy single line (~8s spoken) for {product_name}. "
                         f"Description: {product_description}. Tone: {tone}. Language: {language}. Style: {reel_type}."
            )
            script = resp.text.strip()
            st.subheader("📜 Generated Script")
            st.success(script)

        # ---- Step 2: Image conversion ----
        image_bytes = uploaded_image.read()
        image_input = types.Image(
            image_bytes=image_bytes,
            mime_type="image/png" if uploaded_image.name.endswith("png") else "image/jpeg"
        )

        # ---- Step 3: Video generation (8s, VEO fallback) ----
        veo_prompt = f"Create an 8-second marketing clip (16:9) for social media: {script}. Use the uploaded image with dynamic zoom and motion."
        video_generated = False
        video_path = os.path.join(tempfile.gettempdir(), "reel.mp4")
        operation = None
        model_used = None

        with st.spinner("🎬 Generating video..."):
            try:
                operation = client.models.generate_videos(
                    model="veo-3.0-generate-001",
                    prompt=veo_prompt,
                    image=image_input
                )
                model_used = "VEO-3.0"
            except Exception as e3:
                st.warning(f"⚠️ VEO-3.0 not available, falling back to VEO-2.0... ({e3})")
                try:
                    operation = client.models.generate_videos(
                        model="veo-2.0-generate-001",
                        prompt=veo_prompt,
                        image=image_input
                    )
                    model_used = "VEO-2.0"
                except Exception as e2:
                    st.error(f"❌ Both VEO models failed. Error: {e2}")
                    operation = None

        if operation:
            with st.spinner(f"⏳ Waiting for {model_used} result..."):
                while not operation.done:
                    time.sleep(5)
                    operation = client.operations.get(operation)

            if getattr(operation, "response", None) and getattr(operation.response, "generated_videos", None):
                generated_video = operation.response.generated_videos[0]
                video_bytes = client.files.download(file=generated_video.video)
                with open(video_path, "wb") as f:
                    f.write(video_bytes)
                video_generated = True
                st.success(f"✅ Video generated using {model_used}!")
            else:
                st.error("Video generation finished but no video found in response.")
                st.stop()
        else:
            st.stop()

        # ---- Step 4: Gemini TTS (~8s) ----
        tts_file_path = os.path.join(tempfile.gettempdir(), "tts_voice.wav")
        with st.spinner("🔊 Generating voiceover with Gemini TTS..."):
            try:
                tts_response = client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=f"Speak this line clearly and enthusiastically: {script}",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Kore"
                                )
                            )
                        )
                    )
                )
                audio_data = tts_response.candidates[0].content.parts[0].inline_data.data
                wave_file(tts_file_path, audio_data)
                st.success("🔊 Voiceover generated.")
            except Exception as e:
                st.error(f"Gemini TTS failed: {e}")
                st.stop()

        # ---- Step 5: Merge video + 4s intro + voiceover + bg music (12s) ----
        if video_generated:
            merged_path = os.path.join(tempfile.gettempdir(), "final_reel_12s.mp4")
            try:
                with st.spinner("🎧 Merging final 12s reel..."):
                    vid_clip = VideoFileClip(video_path).subclip(0, 8)
                    intro_clip = ColorClip(size=vid_clip.size, color=(0,0,0), duration=4)
                    final_video = concatenate_videoclips([intro_clip, vid_clip])

                    bg_audio_clip = AudioFileClip(bg_audio_path).volumex(0.25).set_duration(12)
                    voice_clip = AudioFileClip(tts_file_path).set_start(4)

                    final_audio = CompositeAudioClip([bg_audio_clip, voice_clip])
                    final_video = final_video.set_audio(final_audio).set_duration(12)
                    final_video.write_videofile(merged_path, fps=24, codec="libx264", audio_codec="aac", threads=2, verbose=False, logger=None)

                st.success("✅ Final 12s reel ready!")
                st.video(merged_path)

                # ---- Step 6: SEO Title & Description (1 option) ----
                title, desc = generate_youtube_package(client, product_name, script, language)

                # Modern SEO card with horizontal copy buttons
                st.markdown(f"""
                <div style="
                    border:1px solid #ccc; 
                    padding:20px; 
                    border-radius:10px; 
                    margin-top:15px; 
                    background-color:#333; 
                    color:white;
                    font-family:sans-serif;
                ">
                    <h3 style="color:#FFD700; margin-bottom:15px;">SEO Option</h3>
                    <p style="margin-bottom:10px;"><strong>Title:</strong> {title}</p>
                    <p style="margin-bottom:10px;"><strong>Description:</strong> {desc}</p>
                    <div style="display:flex; gap:10px;">
                        <button style="
                            background-color:#FFD700; 
                            color:#333; 
                            border:none; 
                            padding:8px 15px; 
                            border-radius:5px; 
                            cursor:pointer;
                        " 
                        onmouseover="this.style.backgroundColor='#e6c200';" 
                        onmouseout="this.style.backgroundColor='#FFD700';" 
                        onclick="navigator.clipboard.writeText({json.dumps(title)}); alert('Title copied!')">
                            📋 Copy Title
                        </button>

                        <button style="
                            background-color:#FFD700; 
                            color:#333; 
                            border:none; 
                            padding:8px 15px; 
                            border-radius:5px; 
                            cursor:pointer;
                        " 
                        onmouseover="this.style.backgroundColor='#e6c200';" 
                        onmouseout="this.style.backgroundColor='#FFD700';" 
                        onclick="navigator.clipboard.writeText({json.dumps(desc)}); alert('Description copied!')">
                            📋 Copy Description
                        </button>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ---- Step 7: Download button for video at the end ----
                with open(merged_path, "rb") as f:
                    st.download_button("⬇️ Download Video", f, file_name="marketing_reel_12s.mp4")

            except Exception as e:
                st.error(f"Failed to merge/export final reel: {e}")
                st.stop()
























