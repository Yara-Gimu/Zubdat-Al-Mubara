# ⚽ Smart Sports Summary Platform (Zubdat Al-Mubara)

An AI-powered platform that automatically generates concise football match highlight videos by detecting key events such as goals and cards — saving users the time of watching full matches.

**🚀 Live Demo:** [Experience the AI on Hugging Face Spaces](https://huggingface.co/spaces/yuributterfly/Zubdat-Al-Mubara) *(Serverless Docker Deployment)*

---

## 🚀 Project Overview

- **AI Backend:** Python scripts leveraging OpenAI's Whisper model for speech-to-text to extract commentary and detect key events.
- **Cloud Architecture (New!):** Containerized the entire AI application using **Docker** and deployed it seamlessly to **Hugging Face Spaces**. Established a scalable, serverless architecture that handles heavy video processing and FFmpeg dependencies automatically.
- **Frontend:** A simple website built with HTML, CSS, and JavaScript to present the generated video summaries.
- The platform produces **highlight videos only** — no text-based summaries are generated.

---

## 🛠️ Technologies & Libraries

**Cloud & DevOps:**
- `Docker` — Containerization and environment isolation
- `Hugging Face Spaces` — Serverless cloud deployment
- `Flask` — Web framework for creating the API

**AI & Python Libraries:** - `openai-whisper` — Speech-to-text processing  
- `moviepy` — Video editing and concatenation  
- `numpy`, `pandas` — Data handling  
- `tqdm` — Progress bars during processing  
- `ffmpeg-python` — Interfacing with FFmpeg for video operations

**Frontend:** - HTML / CSS / JavaScript for user interface and video playback

---

## ⚙️ Setup & Installation Instructions

### Option 1: Run via Docker (Recommended & Easiest)
No need to install FFmpeg or Python manually! Just use Docker:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Yara-Gimu/Zubdat-Al-Mubara.git](https://github.com/Yara-Gimu/Zubdat-Al-Mubara.git)
   cd Zubdat-Al-Mubara

Build the Docker container:

Bash
docker build -t zubdat-al-mubara .
Run the container:

Bash
docker run -p 7860:7860 zubdat-al-mubara
Open your browser: Go to http://localhost:7860

Option 2: Manual Local Setup
If you prefer running it directly on your machine without Docker:

Create and activate a Python virtual environment:

Windows: python -m venv venv then venv\Scripts\activate

macOS/Linux: python3 -m venv venv then source venv/bin/activate

Install dependencies:

Bash
pip install -r requirements.txt
Install FFmpeg: Download from the official site and add it to your system PATH.

Run the script:

Bash
python highlight_generator.py --input path/to/match.mp4 --output path/to/summary.mp4
📸 Project Demo & Usage Screenshots
Below are screenshots illustrating the key steps of using the Smart Sports Summary Platform:

Website Homepage: The main interface where users start.

Quick Access Button Clicked: Accessing the video upload and summary features quickly.

Dark Mode Activated: Night theme for comfortable viewing.

Video Selected for Processing: Choosing a match video to analyze.

Video Running and Being Analyzed: The backend AI processing the video and extracting highlights.

Summary Video Generated: Final highlight video ready for playback.

🔧 Notes
The project uses the pre-trained Whisper model; no additional training is required.

Only highlight videos are produced — no text summaries.

Make sure to have FFmpeg installed and accessible from your system PATH if running locally without Docker.

👩‍💻 Developer
Yara — Computer Science student at King Abdulaziz University, passionate about AI-driven media solutions and scalable cloud architectures aligned with Saudi Vision 2030.

🌟 Vision
This project enhances sports media consumption by leveraging AI to create accessible, efficient video summaries — empowering fans and media professionals alike.
