from flask import Flask, request, jsonify, render_template, send_file
import whisper
import os
import subprocess
from functools import lru_cache
import warnings
import uuid
import shutil

warnings.filterwarnings("ignore", message="expected np.ndarray")

app = Flask(__name__)
CLIP_DURATION = 10  # عدد الثواني لكل مقطع

# الكلمات المفتاحية كما هي في كودك...
SPORT_KEYWORDS = {
    'Handball': ["goal", "هدف", "قول", "save", "تصدي", "صد", "penalty", "ركلة جزاء", "بلنتي", "fast break", "هجمة مرتدة", "مرتدة سريعة", "turnover", "فقدان الكرة", "خسارة الكرة", "block", "اعتراض", "بلوك"],
    'Martial Arts': ["knockout", "ضربة قاضية", "كي أو", "submission", "اخضاع", "تسليم", "takedown", "طرح أرضًا", "مسكة", "punch", "لكمة", "بوكس", "kick", "ركلة", "شوت", "roundhouse", "ركلة دائرية", "ركلة دوران"],
    'Car Racing': ["overtake", "تجاوز", "عداه", "crash", "حادث", "خبط", "اصطدام", "fastest lap", "أسرع لفة", "أسرع دورة", "pit stop", "توقف للصيانة", "بيت ستوب", "final lap", "اللفة الأخيرة", "الدورة الأخيرة", "victory", "فوز", "ربح", "نصر"],
    'Basketball': ["3-pointer", "ثلاثية", "ثلاث نقاط", "slam dunk", "تغميسة", "دانك", "fast break", "هجمة مرتدة", "مرتدة سريعة", "steal", "سرقة الكرة", "خطف الكرة", "assist", "تمريرة حاسمة", "باص حاسم", "foul", "خطأ", "فاول"],
    'Football': ["goal", "هدف", "قول", "penalty kick", "ركلة جزاء", "بلنتي", "shot", "تسديدة", "شوت", "dangerous attack", "هجمة خطيرة", "هجمة قوية", "corner kick", "ركنية", "ضربة زاوية", "yellow card", "بطاقة صفراء", "كرت أصفر", "red card", "بطاقة حمراء", "كرت أحمر"]
}

@lru_cache(maxsize=1)
def load_whisper_model():
    return whisper.load_model("small")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # إعدادات
    temp_id = str(uuid.uuid4())[:8]
    video_path = f"temp_{temp_id}.mp4"
    audio_path = f"temp_{temp_id}.wav"
    output_dir = f"output_{temp_id}"
    os.makedirs(output_dir, exist_ok=True)

    sport_type = request.form.get('sport_type', 'Football')
    selected_moment = request.form.get('selected_moment')
    keywords = [kw.lower() for kw in SPORT_KEYWORDS.get(sport_type, [])]

    if selected_moment and selected_moment != 'all':
        keywords = [selected_moment.replace('_', ' ')]

    try:
        # حفظ الفيديو
        file.save(video_path)

        # استخراج الصوت بصيغة WAV منخفضة القناة لتسريع Whisper
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "1", "-ar", "16000", audio_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # تشغيل Whisper
        model = load_whisper_model()
        result = model.transcribe(audio_path, fp16=False, verbose=False)

        important_moments = []
        for segment in result["segments"]:
            text = segment["text"].lower()
            if any(keyword in text for keyword in keywords):
                important_moments.append(segment["start"])

        if not important_moments:
            return jsonify({"error": "No highlights found"}), 404

        # تقطيع الفيديو مباشرة باستخدام FFmpeg بدون فقد جودة
        clips_paths = []
        for idx, start in enumerate(sorted(set(important_moments))):
            start_time = max(0, start)
            end_time = start_time + CLIP_DURATION
            clip_output = os.path.join(output_dir, f"clip_{idx}.mp4")

            subprocess.run([
                "ffmpeg", "-y", "-ss", str(start_time), "-i", video_path,
                "-t", str(CLIP_DURATION),
                "-c", "copy", clip_output
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            clips_paths.append(clip_output)

        # دمج المقاطع النهائية
        list_file = os.path.join(output_dir, "clips.txt")
        with open(list_file, "w") as f:
            for clip_path in clips_paths:
                f.write(f"file '{os.path.abspath(clip_path)}'\n")

        final_output = os.path.join(output_dir, "highlights_output.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", final_output
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        response = send_file(
            final_output,
            as_attachment=True,
            mimetype='video/mp4',
            download_name=f"{sport_type}_highlights.mp4"
        )

        @response.call_on_close
        def cleanup():
            try:
                os.remove(video_path)
                os.remove(audio_path)
                shutil.rmtree(output_dir)
            except:
                pass

        return response

    except Exception as e:
        try:
            os.remove(video_path)
            os.remove(audio_path)
            shutil.rmtree(output_dir)
        except:
            pass
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
