from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re

app = Flask(__name__)

# 🔑 Configure Gemini API Key
genai.configure(api_key="AIzaSyD4zQgPTINrNroA76kQgKAjr9ueHTfMfCE")
model = genai.GenerativeModel("gemini-1.5-flash")

# 🔍 Extract video ID
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# 📄 Get YouTube transcript
def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([item['text'] for item in transcript])

# 🧠 Generate script using Gemini
def generate_script(transcript):
    prompt = f"""Create a YouTube script based on this transcript. The script should have:
    - A hooky intro
    - Scene-wise breakdown (Scene 1, Scene 2, etc.)
    - A strong outro and call-to-action

    Transcript:
    {transcript[:6000]}"""

    response = model.generate_content(prompt)
    return response.text

@app.route("/", methods=["GET", "POST"])
def index():
    script_output = None
    error = None

    if request.method == "POST":
        youtube_url = request.form.get("youtube_url")
        try:
            video_id = extract_video_id(youtube_url)
            transcript = get_transcript(video_id)
            script_output = generate_script(transcript)
        except Exception as e:
            error = f"Error: {e}"

    return render_template("index.html", script=script_output, error=error)

if __name__ == "__main__":
    app.run(debug=True)
