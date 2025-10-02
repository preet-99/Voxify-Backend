## 🎙️ Flask Media Processing Backend


- Speech-to-Text (Whisper model or OpenAI API )

- Text-to-Speech (gTTS)

- Image से Text Extraction (OCR via Tesseract) Speech

- Video Trimming और Audio Extraction

- Text File to Speech

---

## 🚀 Features

- 🎥 *Video to Text* – Transcribe spoken content from videos.  
- 🎵 *Audio to Text* – Convert audio files into written transcripts.  
- 🗣 *Text to Speech* – Generate natural speech from written text.  
- 📄 *Text File to Speech* – Upload a text file and listen to its spoken version.  
- 🖼 *Image to Speech* – Extract text from images (OCR) and convert it into speech.  
- ✂ *Video Trimming* – Cut and save specific portions of videos.  

---

## 🛠️ Tech Stack

- *Backend* : Flask (Python)

- *OCR* : Tesseract + Pytesseract

- *Speech Recognition* : Whisper / OpenAI API

- *TTS* : gTTS (Google Text-to-Speech)

- *Video Processing* : FFmpeg, MoviePy

- *Language Detection* : langid, langdetect

---
## 📂 Project Structure  
```text
flask-media-backend/
│── app.py               # Main Flask application
│── requirements.txt     # Dependencies
│── temp/                # Temporary files (auto-created)
│── README.md            # Project documentation
```
---
# 👨‍💻 Authors

- @preet-99 - Preet Vishwakarma
- @harshit2525 - Harshit Aggarwal

---
## ⚙️ Installation

### 1. Clone Repository:

```bash
git clone https://github.com/preet-99/Voxify-Backend.git
cd Voxify-Backend
```

### 2. Create Virtual Environment:

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 4. Other Dependencies:

- For Windows:
   - Install Tesseract OCR
   - Set path
   - pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

- For Linus/Mac:
  - sudo apt install tesseract-ocr





