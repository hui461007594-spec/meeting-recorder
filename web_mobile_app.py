
from flask import Flask, render_template_string, request, jsonify, send_from_directory
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

HTML_TEMPLATE = '''
&lt;!DOCTYPE html&gt;
&lt;html lang="zh-CN"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"&gt;
    &lt;title&gt;会议录音转文字&lt;/title&gt;
    &lt;style&gt;
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            text-align: center;
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .content {
            padding: 20px;
        }
        .section {
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
        }
        .section-title::before {
            content: '';
            width: 4px;
            height: 16px;
            background: #667eea;
            margin-right: 10px;
            border-radius: 2px;
        }
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 10px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .btn-success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .file-input {
            display: none;
        }
        .file-label {
            display: block;
            width: 100%;
            padding: 15px;
            border: 2px dashed #ddd;
            border-radius: 12px;
            text-align: center;
            color: #666;
            cursor: pointer;
            transition: all 0.3s;
        }
        .file-label:hover {
            border-color: #667eea;
            color: #667eea;
        }
        .file-label:active {
            background: #f8f9ff;
        }
        .status {
            padding: 15px;
            background: #f8f9ff;
            border-radius: 12px;
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .status.success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .status.error {
            background: #ffebee;
            color: #c62828;
        }
        .status.loading {
            background: #e3f2fd;
            color: #1565c0;
        }
        .tab-container {
            margin-top: 20px;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #eee;
            margin-bottom: 15px;
        }
        .tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            cursor: pointer;
            font-size: 14px;
            color: #666;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        textarea {
            width: 100%;
            min-height: 200px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.6;
            resize: vertical;
            font-family: inherit;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .recording-indicator {
            display: none;
            align-items: center;
            justify-content: center;
            padding: 10px;
            background: #ffebee;
            border-radius: 12px;
            margin-bottom: 10px;
        }
        .recording-indicator.active {
            display: flex;
        }
        .pulse {
            width: 12px;
            height: 12px;
            background: #f5576c;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .recording-text {
            color: #c62828;
            font-weight: 600;
        }
        .settings {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .settings select {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 10px;
            font-size: 14px;
            background: white;
        }
        .save-btn {
            display: flex;
            gap: 10px;
        }
        .save-btn .btn {
            flex: 1;
        }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;div class="container"&gt;
        &lt;div class="header"&gt;
            &lt;h1&gt;🎙️ 会议录音转文字&lt;/h1&gt;
            &lt;p&gt;录音 → 文字 → 会议记录 → 待办事项&lt;/p&gt;
        &lt;/div&gt;
        &lt;div class="content"&gt;
            &lt;div class="section"&gt;
                &lt;div class="section-title"&gt;设置&lt;/div&gt;
                &lt;div class="settings"&gt;
                    &lt;select id="modelSelect"&gt;
                        &lt;option value="tiny"&gt;tiny (最快)&lt;/option&gt;
                        &lt;option value="base" selected&gt;base (推荐)&lt;/option&gt;
                        &lt;option value="small"&gt;small (较准)&lt;/option&gt;
                        &lt;option value="medium"&gt;medium (准确)&lt;/option&gt;
                    &lt;/select&gt;
                    &lt;select id="languageSelect"&gt;
                        &lt;option value="zh" selected&gt;中文&lt;/option&gt;
                        &lt;option value="en"&gt;英文&lt;/option&gt;
                    &lt;/select&gt;
                &lt;/div&gt;
            &lt;/div&gt;

            &lt;div class="section"&gt;
                &lt;div class="section-title"&gt;录音/上传&lt;/div&gt;
                &lt;div class="recording-indicator" id="recordingIndicator"&gt;
                    &lt;div class="pulse"&gt;&lt;/div&gt;
                    &lt;span class="recording-text"&gt;正在录音...&lt;/span&gt;
                &lt;/div&gt;
                &lt;button class="btn btn-danger" id="recordBtn" onclick="toggleRecording()"&gt;
                    🎤 开始录音
                &lt;/button&gt;
                &lt;label class="file-label" for="fileInput"&gt;
                    📁 选择音频文件
                &lt;/label&gt;
                &lt;input type="file" id="fileInput" class="file-input" accept="audio/*" onchange="handleFileSelect(event)"&gt;
            &lt;/div&gt;

            &lt;div class="section"&gt;
                &lt;button class="btn btn-primary" id="processBtn" onclick="processAudio()" disabled&gt;
                    ⚡ 开始处理
                &lt;/button&gt;
            &lt;/div&gt;

            &lt;div class="status" id="status"&gt;
                准备就绪
            &lt;/div&gt;

            &lt;div class="tab-container" id="resultsContainer" style="display: none;"&gt;
                &lt;div class="section-title"&gt;处理结果&lt;/div&gt;
                &lt;div class="tabs"&gt;
                    &lt;div class="tab active" onclick="switchTab(0)"&gt;转录文本&lt;/div&gt;
                    &lt;div class="tab" onclick="switchTab(1)"&gt;会议记录&lt;/div&gt;
                    &lt;div class="tab" onclick="switchTab(2)"&gt;待办事项&lt;/div&gt;
                &lt;/div&gt;
                &lt;div class="tab-content active" id="tab0"&gt;
                    &lt;textarea id="transcript" readonly&gt;&lt;/textarea&gt;
                &lt;/div&gt;
                &lt;div class="tab-content" id="tab1"&gt;
                    &lt;textarea id="minutes" readonly&gt;&lt;/textarea&gt;
                &lt;/div&gt;
                &lt;div class="tab-content" id="tab2"&gt;
                    &lt;textarea id="todos" readonly&gt;&lt;/textarea&gt;
                &lt;/div&gt;
                &lt;div class="save-btn"&gt;
                    &lt;button class="btn btn-success" onclick="downloadAll()"&gt;
                        💾 保存全部
                    &lt;/button&gt;
                &lt;/div&gt;
            &lt;/div&gt;
        &lt;/div&gt;
    &lt;/div&gt;

    &lt;script&gt;
        let mediaRecorder = null;
        let audioChunks = [];
        let audioBlob = null;
        let currentResult = null;

        async function toggleRecording() {
            const btn = document.getElementById('recordBtn');
            const indicator = document.getElementById('recordingIndicator');
            
            if (!mediaRecorder) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) =&gt; {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () =&gt; {
                        audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        document.getElementById('processBtn').disabled = false;
                        updateStatus('录音已完成，点击开始处理');
                    };
                    
                    mediaRecorder.start();
                    btn.textContent = '⏹️ 停止录音';
                    indicator.classList.add('active');
                    updateStatus('正在录音...', 'loading');
                } catch (err) {
                    updateStatus('无法访问麦克风: ' + err.message, 'error');
                }
            } else {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track =&gt; track.stop());
                mediaRecorder = null;
                btn.textContent = '🎤 开始录音';
                indicator.classList.remove('active');
            }
        }

        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                audioBlob = file;
                document.getElementById('processBtn').disabled = false;
                updateStatus('已选择文件: ' + file.name);
            }
        }

        async function processAudio() {
            if (!audioBlob) {
                updateStatus('请先录音或选择文件', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('model', document.getElementById('modelSelect').value);
            formData.append('language', document.getElementById('languageSelect').value);

            document.getElementById('processBtn').disabled = true;
            updateStatus('正在处理中，请稍候...', 'loading');

            try {
                const response = await fetch('/api/transcribe', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    currentResult = result;
                    document.getElementById('transcript').value = result.transcript;
                    document.getElementById('minutes').value = result.minutes;
                    document.getElementById('todos').value = result.todos;
                    document.getElementById('resultsContainer').style.display = 'block';
                    updateStatus('处理完成！', 'success');
                } else {
                    updateStatus('处理失败: ' + result.error, 'error');
                }
            } catch (err) {
                updateStatus('网络错误: ' + err.message, 'error');
            } finally {
                document.getElementById('processBtn').disabled = false;
            }
        }

        function switchTab(index) {
            document.querySelectorAll('.tab').forEach((tab, i) =&gt; {
                tab.classList.toggle('active', i === index);
            });
            document.querySelectorAll('.tab-content').forEach((content, i) =&gt; {
                content.classList.toggle('active', i === index);
            });
        }

        function updateStatus(message, type = '') {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status ' + type;
        }

        function downloadText(text, filename) {
            const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }

        function downloadAll() {
            if (!currentResult) return;
            
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            downloadText(currentResult.transcript, 'transcript_' + timestamp + '.txt');
            downloadText(currentResult.minutes, 'minutes_' + timestamp + '.txt');
            downloadText(currentResult.todos, 'todos_' + timestamp + '.txt');
            updateStatus('文件已保存！', 'success');
        }
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
'''


def get_converter(model_size="base"):
    global audio_converter
    if audio_converter is None:
        audio_converter = AudioToText(model_size=model_size)
    return audio_converter


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


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
    print("=" * 60)
    print("会议录音转文字 - 移动端Web应用")
    print("=" * 60)
    print()
    print("使用方法:")
    print("1. 确保手机和电脑在同一WiFi网络")
    print("2. 在手机浏览器中访问: http://电脑IP:5000")
    print()
    print("服务已启动，按 Ctrl+C 停止")
    print("=" * 60)
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
