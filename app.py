from flask import Flask, render_template, request, send_file, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    video_url = request.form.get('video_url')  # Video URL'yi alıyoruz
    language = request.form.get('language', 'en')  # Varsayılan dil 'en' (İngilizce)

    if not video_url:
        return jsonify({'success': False, 'error': 'Video URL is required!'}), 400

    try:
        # YouTube video ID'sini URL'den çıkartıyoruz
        if "v=" in video_url:
            video_id = video_url.split('v=')[-1].split('&')[0]
        else:
            return jsonify({'success': False, 'error': ' Geçersiz format!'}), 400

        # Transkripti almak için YouTubeTranscriptApi kullanıyoruz
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])  # Dil parametresi ekledik
        transcript_text = "\n".join([item['text'] for item in transcript])

        # Transkripti dosyaya kaydediyoruz
        file_path = f"transcripts/{video_id}.txt"
        os.makedirs('transcripts', exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(transcript_text)

        return jsonify({'success': True, 'file_path': file_path})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<video_id>')
def download(video_id):
    file_path = f"transcripts/{video_id}.txt"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
