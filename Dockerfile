FROM python:3.9-slim

# تثبيت أداة FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# إنشاء مستخدم عادي بصلاحيات آمنة (متطلب إجباري في Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# نسخ ملف المتطلبات وتثبيتها
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY --chown=user . .

# فتح البوابة الخاصة بـ Hugging Face
ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]