
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from audio_to_text import AudioToText
from meeting_processor import MeetingProcessor
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

audio_converter = None
meeting_processor = MeetingProcessor()


def get_converter(model_size="base"):
    global audio_converter
    if audio_converter is None:
        audio_converter = AudioToText(model_size=model_size)
    return audio_converter


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "没有音频文件"}), 400
        
        audio_file = request.files['audio']
        model_size = request.form.get('model', 'base')
        language = request.form.get('language', 'zh')
        
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = f"{uuid.uuid4()}_{audio_file.filename}"
        filepath = os.path.join(temp_dir, filename)
        audio_file.save(filepath)
        
        converter = get_converter(model_size)
        result = converter.transcribe(filepath, language=language)
        
        transcript = result["text"]
        minutes = meeting_processor.generate_minutes(transcript)
        todos = meeting_processor.extract_todos(transcript, minutes)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        transcript_path = os.path.join(output_dir, f"transcript_{timestamp}.txt")
        minutes_path = os.path.join(output_dir, f"minutes_{timestamp}.txt")
        todos_path = os.path.join(output_dir, f"todos_{timestamp}.txt")
        
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)
        with open(minutes_path, "w", encoding="utf-8") as f:
            f.write(minutes)
        with open(todos_path, "w", encoding="utf-8") as f:
            f.write(todos)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            "success": True,
            "transcript": transcript,
            "minutes": minutes,
            "todos": todos
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
