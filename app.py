from flask import Flask, render_template, request, redirect, url_for
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from pathlib import Path
from pytube import YouTube
import requests
import re
from moviepy.editor import *
from moviepy.audio.io import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from werkzeug.utils import secure_filename
from mailId import mailid
from mailId import password

app = Flask(__name__)

# Configuration for email
mailid = mailid
password = password

# Directory to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        singer = request.form['singer']
        seconds = int(request.form['seconds'])
        num = int(request.form['num'])
        result_filename = request.form['result_filename']

        folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
        if not os.path.isdir(folder):
            os.makedirs(folder)

        links = get_links(singer)[:num]
        folderz(folder, links)
        to_audio(folder)
        trim_audio(folder, seconds)
        result_filename = joining_audio_files(folder, result_filename)

        # Send email with the result
        send_email(mailid, password, result_filename)

        return "Video mashup complete. Check your email for the result."

    return render_template('index.html')

def get_links(query):
    # ... Your existing code ...
    query = query.replace(' ', '+')
    url = f"https://www.youtube.com/results?search_query={query}"
    response = requests.get(url)
    html = response.text
    links = re.findall('"/watch\?v=(.{11})"', html)
    return [f"https://www.youtube.com/watch?v={link}" for link in links]

def downloading_videos(link, folder):
    # ... Your existing code ...
    yt = YouTube(link)
    stream = yt.streams.first()
    stream.download(folder)
    print("Video downloaded successfully")

def to_audio(folder):
    # ... Your existing code ...
    for filename in os.listdir(folder):
        if filename.endswith(".3gpp"):
            video = VideoFileClip(os.path.join(folder, filename))
            audio = video.audio
            audio.write_audiofile(os.path.join(folder, filename.split(".")[0] + ".mp3"))
            print("Converted {} to audio successfully".format(filename))

def trim_audio(folder, seconds):
    # ... Your existing code ...
    for audio_file in os.listdir(folder):
        if audio_file.endswith(".mp3"):
            audio_path = os.path.join(folder, audio_file)
            cut_audio_path = os.path.join(folder, audio_file)
        # Load the audio file
            audio = AudioFileClip(audio_path)

        # Cut the audio to the specified duration
            #cut_audio = audio.subclip(seconds, audio.duration)
            cut_audio = audio.subclip(0,seconds)

        # Save the cut audio to a file
            cut_audio.write_audiofile(cut_audio_path)
def joining_audio_files(folder, output_filename):
    # ... Your existing code ...
    audio_clips = []
    for filename in os.listdir(folder):
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            audio_clips.append(AudioFileClip(os.path.join(folder, filename)))
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(output_filename)
    print("Merged all audio files in the folder successfully")
    return output_filename

def folderz(folder, links):
    # ... Your existing code ...
    if not os.path.isdir(folder):
        os.makedirs(folder)
    for link in links:
        downloading_videos(link, folder)

def send_email(mailid, password, attachment_path):
    message = MIMEMultipart()
    message["from"] = "Kishan Pandey"
    message["to"] = "recipient_email@gmail.com"  # Change this to the recipient's email
    message["subject"] = "This is for you..."
    message.attach(MIMEAudio(Path(os.path.realpath(attachment_path)).read_bytes(), _subtype="mpeg"))

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(mailid, password)
        smtp.send_message(message)
        print("Sent...")

if __name__ == "__main__":
    app.run(debug=True)
