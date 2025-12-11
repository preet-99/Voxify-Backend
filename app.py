from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import whisper  # For local Whisper model
import moviepy as mp
import tempfile
from gtts.lang import tts_langs
from langdetect import detect, LangDetectException
import subprocess
import os
import io
from gtts import gTTS
import speech_recognition as sr
import pytesseract
import langid
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024 
   
# Load local Whisper model
model = whisper.load_model("large-v2")



#  OpenAI Whisper API,
# openai.api_key = os.getenv("OPENAI_API_KEY")  

# Route 
@app.route("/", methods=["GET"])
def home():
    info = {"name": "preet", "age": "20", "profession": "Coder"}
    return jsonify(info)

# Audio to text
@app.route("/audio_to_text", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file part in the request"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            audio_file.save(temp_audio.name)
            temp_path = temp_audio.name

        # Transcribe
        result = model.transcribe(temp_path, language="hi", task="translate")
        transcribed_text = result["text"]

        # Clean up
        os.remove(temp_path)

        return jsonify({"text": transcribed_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Video to text
@app.route("/video_to_text", methods=["POST"])
def transcribe_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file part in the request"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            video_file.save(temp_video.name)
            video_path = temp_video.name

        # Extract audio
        video = mp.VideoFileClip(video_path)
        audio_path = video_path.replace(".mp4", ".wav")
        video.audio.write_audiofile(audio_path)
        video.close()

        # Transcribe
        result = model.transcribe(audio_path, language="hi", task="translate")
        transcribed_text = result["text"]

        # Clean up
        os.remove(video_path)
        os.remove(audio_path)

        return jsonify({"text": transcribed_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Image to speech
@app.route("/image_to_speech", methods=["POST"])
def image_to_speech():
    if "image" not in request.files:
        return "No image part in the request", 400

    file = request.files["image"]
    if file.filename == "":
        return "No selected file", 400

    try:
        # Load image using PIL
        img = Image.open(file.stream)
    except Exception as e:
        return f"Error opening image file: {e}", 400

    try:
        # Read text from given image
        text = pytesseract.image_to_string(img)
        if not text.strip():
            return "Could not find any text in the image.", 400
    except Exception as e:
        return f"Error during OCR: {e}", 500

    try:
        # Detect language
        detected_lang, _ = langid.classify(text)  # Extract language code from tuple
        # Check if detected language is supported by gTTS
        supported_langs = tts_langs()
        if detected_lang not in supported_langs.keys():
            return (
                f"Detected language '{detected_lang}' is not supported by gTTS. Supported Languages: {list(supported_langs.keys())}",
                400,
            )
    except Exception as e:
        return f"Error detecting language: {e}", 500

    # Text to speech
    try:
        tts = gTTS(text=text, lang=detected_lang, slow=False, tld="co.in")
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)

        # Send file to the frontend
        return send_file(
            audio_stream, mimetype="audio/mpeg", download_name="extracted_audio.mp3"
        )
    except Exception as e:
        return f"Error generating speech: {e}", 500

# Text File to Speech
@app.route("/text_file_to_speech", methods=["POST"])
def text_file_to_speech():
    if "text_file" not in request.files:
        return {"error": "No text file part in the request"}, 400

    file = request.files["text_file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    if not file.filename.endswith(".txt"):
        return {"error": "File must be a .txt file"}, 400

    try:
        text = file.read().decode("utf-8")
        if not text.strip():
            return {"error": "Text file is empty"}, 400
    except UnicodeDecodeError:
        try:
            text = file.read().decode("latin-1")  # Fallback encoding
            if not text.strip():
                return {"error": "Text file is empty"}, 400
        except UnicodeDecodeError:
            return {"error": "Unsupported text file encoding"}, 400
    except Exception as e:
        return {"error": f"Error reading text file: {str(e)}"}, 500

    try:
        detected_lang, _ = langid.classify(text)
        supported_langs = tts_langs()
        if detected_lang not in supported_langs.keys():
            return {
                "error": f"Detected language '{detected_lang}' is not supported by gTTS. Supported Languages: {list(supported_langs.keys())}"
            }, 400
    except Exception as e:
        return {"error": f"Error detecting language: {str(e)}"}, 500

    try:
        tts = gTTS(text=text, lang=detected_lang, slow=False, tld="co.in")
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        return send_file(
            audio_stream,
            mimetype="audio/mpeg",
            download_name="generated_speech.mp3"
        )
    except Exception as e:
        return {"error": f"Error generating speech: {str(e)}"}, 500


# Video Trim 
@app.route("/trim_video", methods=["POST"])
def trim_video():
    if "video" not in request.files:
        return "No video part in the request", 400

    file = request.files["video"]
    if file.filename == "":
        return "No selected file", 400

    start_time = request.form.get("start_time")
    end_time = request.form.get("end_time")

    try:
        start_time = float(start_time)
        end_time = float(end_time)
    except:
        return "Start and end time must be valid numbers", 400

    try:
        # Save uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            file.save(temp_video.name)
            temp_video_path = temp_video.name

        # Load video
        video = mp.VideoFileClip(temp_video_path)
        if end_time > video.duration:
            video.close()
            os.remove(temp_video_path)
            return f"End time exceeds video duration ({video.duration:.2f}s).", 400

        # Trim
        trimmed = video.subclipped(start_time, end_time) 

        # Save to output file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as output_file:
            output_path = output_file.name
        trimmed.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

        # Read into memory
        with open(output_path, "rb") as f:
            video_bytes = f.read()

        # Cleanup
        video.close()
        trimmed.close()
        os.remove(temp_video_path)
        os.remove(output_path)

        return send_file(
            io.BytesIO(video_bytes),
            mimetype="video/mp4",
            as_attachment=True,
            download_name="trimmed_video.mp4"
        )

    except Exception as e:
        return f"Error trimming video: {e}", 500
    
# Video to Audio 
@app.route("/video_to_audio", methods=["POST"])
def video_to_audio():
    if "video" not in request.files:
        return jsonify({"error": "No video file part in the request"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    os.makedirs("temp", exist_ok=True)
    video_path = os.path.join("temp", video_file.filename)
    video_file.save(video_path)

    audio_path = os.path.join("temp", "output_audio.mp3")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-q:a",
                "0",
                "-map",
                "a",
                audio_path,
            ],
            check=True,
        )

        # Validate audio file exists and is non-empty
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            return jsonify({"error": "No audio track found in video"}), 400

        # Send the audio file with correct MIME type
        response = send_file(
            audio_path,
            as_attachment=True,
            download_name="extracted_audio.mp3",
            mimetype="audio/mpeg",
        )

        # Clean up files after sending
        try:
            os.remove(video_path)
            os.remove(audio_path)
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")

        return response

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"FFmpeg error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Text to Speech 
@app.route("/tts", methods=["POST"])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text.strip():
            return jsonify({"error": "No text provided"}), 400

        # Try to detect language
        try:
            detected_lang = detect(text)
        except LangDetectException:
            detected_lang = "en"  # fallback if detection fails

        # Supported languages in gTTS
        supported_langs = tts_langs()

        # If detected language is not supported → fallback to English
        lang = detected_lang if detected_lang in supported_langs else "en"

        # Debug print (optional)
        print(f"Text: {text} | Detected: {detected_lang} | Using: {lang}")

        # Generate speech
        tts = gTTS(text=text, lang=lang,slow=False, tld="co.in")
        audio_file = io.BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)

        return send_file(
            audio_file,
            mimetype="audio/mpeg",
            as_attachment=True,
            download_name="generated_speech.mp3",
        )
    except Exception as e:
        return jsonify({"error": f"TTS failed: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=True)
