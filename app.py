from flask import Flask, render_template, request, jsonify, send_file
import os
import yt_dlp
import subprocess
import sys
from werkzeug.utils import secure_filename
import requests
from mutagen import File
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from io import BytesIO

app = Flask(__name__)

# Configuration
DOWNLOAD_FOLDER = "downloads"
ALLOWED_EXTENSIONS = {'mp3'}

# Créer le dossier de téléchargement s'il n'existe pas
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def check_ffmpeg():
    """Vérifie si ffmpeg est installé et accessible"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def sanitize_filename(filename):
    """Nettoie le nom de fichier"""
    invalid_chars = '<>:"/\\|?*\n\r'
    filename = filename.strip()
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    while '__' in filename:
        filename = filename.replace('__', '_')
    return filename

def add_metadata_to_mp3(mp3_path, video_info):
    """Ajoute les métadonnées et l'image à un fichier MP3"""
    try:
        # Créer un objet ID3 s'il n'existe pas
        try:
            audio = ID3(mp3_path)
        except ID3HeaderError:
            audio = ID3()
        
        # Ajouter le titre
        audio['TIT2'] = TIT2(encoding=3, text=video_info['title'])
        
        # Ajouter l'artiste
        audio['TPE1'] = TPE1(encoding=3, text=video_info['channel'])
        
        # Ajouter l'album
        audio['TALB'] = TALB(encoding=3, text="YouTube")
        
        # Récupérer et ajouter l'image
        if 'thumbnail' in video_info and video_info['thumbnail']:
            try:
                response = requests.get(video_info['thumbnail'])
                if response.status_code == 200:
                    image_data = response.content
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,  # 3 est pour l'image de couverture
                        desc='Cover',
                        data=image_data
                    )
            except Exception as e:
                print(f"Erreur lors de l'ajout de l'image : {str(e)}")
        
        # Sauvegarder les métadonnées
        audio.save(mp3_path, v2_version=3)
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout des métadonnées : {str(e)}")
        return False

def search_videos(query):
    """Recherche des vidéos YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Réactivé pour une recherche plus rapide
        'default_search': 'ytsearch5:',
        'no_check_certificates': True,
        'prefer_insecure': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch5:{query}", download=False)['entries']
            valid_results = []
            
            for result in results:
                try:
                    # Vérifier si la vidéo est téléchargeable
                    if result.get('is_live') or result.get('availability') == 'private':
                        continue
                    
                    # Utiliser la miniature de plus petite taille (default.jpg)
                    video_id = result.get('id', '')
                    thumbnail = f"https://img.youtube.com/vi/{video_id}/default.jpg"
                    
                    valid_results.append({
                        'title': result['title'],
                        'channel': result['channel'],
                        'url': result['url'],
                        'thumbnail': thumbnail
                    })
                except Exception as e:
                    continue
            
            return valid_results
    except Exception as e:
        print(f"Erreur lors de la recherche : {str(e)}")
        return []

def download_mp3(url):
    """Télécharge et convertit une vidéo YouTube en MP3"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'no_check_certificates': True,
            'prefer_insecure': True,
            'format_sort': ['abr:320'],
            'postprocessor_args': [
                '-codec:a', 'libmp3lame',
                '-q:a', '0',
                '-b:a', '320k',
            ],
            'writesubtitles': False,
            'writeautomaticsub': False,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            clean_title = sanitize_filename(info['title'])
            mp3_filename = f"{clean_title}.mp3"
            mp3_path = os.path.join(DOWNLOAD_FOLDER, mp3_filename)
            
            # Récupérer la meilleure qualité d'image disponible
            thumbnail = info.get('thumbnail', '')
            if not thumbnail:
                # Essayer de récupérer la meilleure qualité d'image disponible
                thumbnails = info.get('thumbnails', [])
                if thumbnails:
                    # Trier par résolution et prendre la plus haute
                    thumbnails.sort(key=lambda x: x.get('width', 0) * x.get('height', 0), reverse=True)
                    thumbnail = thumbnails[0].get('url', '')
            
            # Ajouter les métadonnées
            video_info = {
                'title': info['title'],
                'channel': info['channel'],
                'thumbnail': thumbnail
            }
            add_metadata_to_mp3(mp3_path, video_info)
            
            return mp3_filename
    except Exception as e:
        print(f"Erreur lors du téléchargement : {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_videos(query)
    return jsonify(results)

@app.route('/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL manquante'}), 400
    
    filename = download_mp3(url)
    if not filename:
        return jsonify({'error': 'Erreur lors du téléchargement'}), 500
    
    return jsonify({
        'success': True,
        'filename': filename
    })

@app.route('/downloads/<filename>')
def get_file(filename):
    try:
        return send_file(
            os.path.join(DOWNLOAD_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': 'Fichier non trouvé'}), 404

if __name__ == '__main__':
    if not check_ffmpeg():
        print("⚠️ FFmpeg n'est pas installé. Veuillez l'installer pour utiliser l'application.")
        sys.exit(1)
    app.run(debug=True)