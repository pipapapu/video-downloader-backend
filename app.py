from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/api/download', methods=['POST'])
def get_download_link():
    data = request.json
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({"error": "URL tidak boleh kosong"}), 400

    # Menggunakan UUID agar nama file unik di server
    unique_id = str(uuid.uuid4())
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{unique_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'best', # Mengambil kualitas terbaik video+audio terintegrasi
        'outtmpl': outtmpl,
        'noplaylist': True,
        # Opsi tambahan untuk melewati proteksi beberapa platform
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Ekstrak informasi dan unduh file ke server terlebih dahulu
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'Video')
            ext = info.get('ext', 'mp4')
            
            # Kirim balik informasi file ke APK
            # Di produksi, Anda bisa langsung streaming file atau memberikan direct link download
            return jsonify({
                "status": "success",
                "title": title,
                "file_name": f"{unique_id}.{ext}"
            })
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint untuk mengambil file video murni oleh APK
@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File tidak ditemukan"}), 404

if __name__ == '__main__':
    # Jalankan server di port 5000
    app.run(host='0.0.0.0', port=7860, debug=True)