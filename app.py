import os
from flask import Flask, request, send_file
# شلنا كود مسار المجلد (sys.path) لأنه يسبب مشاكل في السحابة (Docker)
from Test1 import process_match_video 

app = Flask(__name__)

UPLOAD_FOLDER = 'temp_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    return send_file('index.html')

@app.route('/upload', methods=['POST'])
def summarize_video():
    # تعديل مهم: هنا نقرأ "نوع الرياضة" اللي اختاره المستخدم من الواجهة
    sport_type = request.form.get('sport_type', 'Football')

    # الخطأ كان هنا: الواجهة ترسل الملف باسم 'file' وليس 'video'
    if 'file' not in request.files:
        return {"error": "الرجاء إرفاق ملف فيديو"}, 400
        
    file = request.files['file']
    
    if file.filename == '':
        return {"error": "لم يتم اختيار ملف"}, 400

    # حفظ الفيديو الأصلي
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    
    output_path = os.path.join(UPLOAD_FOLDER, "summary_" + file.filename)

    try:
        # نرسل الفيديو للذكاء الاصطناعي مع "نوع الرياضة" عشان يبحث عن الكلمات الصح
        process_match_video(input_path, output_path, sport_type=sport_type)
        
        return send_file(output_path, as_attachment=True)
        
    # الخطأ الثاني كان هنا: كلمة except كانت بمسافة خاطئة وتسبب SyntaxError
    except Exception as e:
        return {"error": f"حدث خطأ أثناء المعالجة: {str(e)}"}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)