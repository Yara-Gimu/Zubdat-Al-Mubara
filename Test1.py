import whisper
import os
import subprocess
from functools import lru_cache
import warnings
import shutil

warnings.filterwarnings("ignore", message="expected np.ndarray")
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

def process_match_video(input_video_path, output_video_path, sport_type='Football'):
    """
    معالجة فيديو المباراة واستخراج اللحظات المهمة
    
    Args:
        input_video_path: مسار الفيديو الأصلي
        output_video_path: مسار حفظ الفيديو الملخص
        sport_type: نوع الرياضة (Football, Basketball, Handball, etc)
    """
    print("جاري معالجة الفيديو واستخراج الأحداث المهمة...")
    
    CLIP_DURATION = 10  # عدد الثواني لكل مقطع
    
    # استخراج اسم الملف والمجلد
    output_dir = os.path.dirname(output_video_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # إنشاء مسارات مؤقتة
    temp_audio = input_video_path.replace('.mp4', '_temp_audio.wav')
    
    try:
        # استخراج الصوت بصيغة WAV منخفضة القناة لتسريع Whisper
        subprocess.run([
            "ffmpeg", "-y", "-i", input_video_path,
            "-ac", "1", "-ar", "16000", temp_audio
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # تشغيل Whisper
        model = load_whisper_model()
        result = model.transcribe(temp_audio, fp16=False, verbose=False)

        # استخراج الكلمات المفتاحية بناءً على نوع الرياضة
        keywords = [kw.lower() for kw in SPORT_KEYWORDS.get(sport_type, [])]
        
        important_moments = []
        for segment in result["segments"]:
            text = segment["text"].lower()
            if any(keyword in text for keyword in keywords):
                important_moments.append(segment["start"])

        if not important_moments:
            print("لم يتم العثور على لحظات مهمة!")
            return False

        print(f"تم العثور على {len(set(important_moments))} لحظة مهمة")

        # تقطيع الفيديو مباشرة باستخدام FFmpeg بدون فقد جودة
        clips_paths = []
        clips_dir = os.path.join(output_dir, "temp_clips")
        os.makedirs(clips_dir, exist_ok=True)
        
        for idx, start in enumerate(sorted(set(important_moments))):
            start_time = max(0, start)
            clip_output = os.path.join(clips_dir, f"clip_{idx}.mp4")

            subprocess.run([
                "ffmpeg", "-y", "-ss", str(start_time), "-i", input_video_path,
                "-t", str(CLIP_DURATION),
                "-c", "copy", clip_output
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            clips_paths.append(clip_output)

        print(f"تم تقطيع {len(clips_paths)} مقطع")

        # دمج المقاطع النهائية
        list_file = os.path.join(clips_dir, "clips.txt")
        with open(list_file, "w") as f:
            for clip_path in clips_paths:
                f.write(f"file '{os.path.abspath(clip_path)}'\n")

        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy", output_video_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        print(f"تم حفظ الفيديو الملخص في: {output_video_path}")
        
        # تنظيف الملفات المؤقتة
        try:
            os.remove(temp_audio)
            shutil.rmtree(clips_dir)
        except:
            pass
        
        return True

    except Exception as e:
        print(f"حدث خطأ أثناء المعالجة: {str(e)}")
        # تنظيف الملفات المؤقتة في حالة الخطأ
        try:
            os.remove(temp_audio)
            shutil.rmtree(clips_dir, ignore_errors=True)
        except:
            pass
        raise
