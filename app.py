from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, current_app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import yt_dlp
import subprocess
import sys
from werkzeug.utils import secure_filename
import requests
from mutagen import File
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from PIL import Image
from datetime import datetime
import time
import shutil
from celery import Celery
from celery.schedules import crontab
import re
import urllib.parse

# Configuration
DOWNLOAD_FOLDER = "downloads"
ALLOWED_EXTENSIONS = {'mp3'}
UPLOAD_FOLDER = "static/uploads/profiles"
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
FILE_RETENTION_HOURS = 24  # Les fichiers seront supprimés après 24h

# Configuration Celery
celery = Celery('youtube_downloader',
                broker='redis://localhost:6379/0',
                backend='redis://localhost:6379/0')

# Configurer les tâches périodiques
celery.conf.beat_schedule = {
    'cleanup-every-hour': {
        'task': 'app.cleanup_old_files',
        'schedule': crontab(minute=0)  # Toutes les heures
    }
}

# Structure pour stocker les logs
download_logs = []

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clé secrète pour les sessions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Configuration du dossier d'upload
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')

# Initialisation du gestionnaire de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Créer les dossiers nécessaires
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Créer une image par défaut si elle n'existe pas
default_profile_path = os.path.join('static', 'default-profile.png')
if not os.path.exists(default_profile_path):
    # Créer une image grise de 200x200 pixels
    img = Image.new('RGB', (200, 200), color='#CCCCCC')
    img.save(default_profile_path)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_profile_image(file, username):
    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        filename = secure_filename(f"{username}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Redimensionner l'image
        img = Image.open(file)
        img.thumbnail((200, 200))  # Taille maximale de 200x200 pixels
        img.save(filepath, quality=85)
        
        return filename
    return None

# Utilisateurs prédéfinis
users = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'role': 'admin',
        'display_name': 'Administrateur',
        'profile_image': None,
        'bio': 'Administrateur du système',
        'download_quota': 0  # 0 = illimité pour les administrateurs
    },
    'user': {
        'password': generate_password_hash('user123'),
        'role': 'user',
        'display_name': 'Utilisateur',
        'profile_image': None,
        'bio': '',
        'download_quota': 100  # Quota par défaut de 100 téléchargements
    }
}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Accès non autorisé')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.role = users[username]['role']
        self.display_name = users[username].get('display_name', username)
        self.profile_image = users[username].get('profile_image')
        self.bio = users[username].get('bio', '')
        self.download_quota = users[username].get('download_quota', 100)  # Quota par défaut de 100

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username]['password'], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Nom d\'utilisateur ou mot de passe incorrect')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template('admin.html', users=users, download_logs=download_logs)

@app.route('/admin/user/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    quota = int(request.form.get('quota', 100))  # Quota par défaut de 100
    
    if username in users:
        flash('Ce nom d\'utilisateur existe déjà', 'error')
        return redirect(url_for('admin'))
    
    users[username] = {
        'password': generate_password_hash(password),
        'role': role,
        'download_quota': 0 if role == 'admin' else quota
    }
    flash('Utilisateur créé avec succès', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/user/edit', methods=['POST'])
@login_required
@admin_required
def edit_user():
    username = request.form.get('username')
    new_password = request.form.get('password')
    new_role = request.form.get('role')
    new_quota = request.form.get('quota')
    
    if username not in users:
        flash('Utilisateur non trouvé')
        return redirect(url_for('admin'))
    
    if new_password:
        users[username]['password'] = generate_password_hash(new_password)
    if new_role:
        users[username]['role'] = new_role
        # Mettre à jour le quota en fonction du rôle
        users[username]['download_quota'] = 0 if new_role == 'admin' else int(new_quota or 100)
    elif new_quota and users[username]['role'] != 'admin':
        users[username]['download_quota'] = int(new_quota)
    
    flash('Utilisateur modifié avec succès')
    return redirect(url_for('admin'))

@app.route('/admin/user/delete', methods=['POST'])
@login_required
@admin_required
def delete_user():
    username = request.form.get('username')
    
    if username not in users:
        flash('Utilisateur non trouvé')
        return redirect(url_for('admin'))
    
    if username == 'admin':
        flash('Impossible de supprimer l\'administrateur principal')
        return redirect(url_for('admin'))
    
    del users[username]
    flash('Utilisateur supprimé avec succès')
    return redirect(url_for('admin'))

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    username = current_user.id
    display_name = request.form.get('display_name')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    bio = request.form.get('bio')
    
    # Vérifier le mot de passe actuel si un nouveau est fourni
    if new_password:
        if not current_password or not check_password_hash(users[username]['password'], current_password):
            flash('Mot de passe actuel incorrect')
            return redirect(url_for('settings'))
        users[username]['password'] = generate_password_hash(new_password)
    
    # Mettre à jour le nom d'affichage
    if display_name:
        users[username]['display_name'] = display_name
    
    # Mettre à jour la bio
    if bio is not None:
        users[username]['bio'] = bio
    
    # Gérer l'upload de l'image de profil
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file.filename:
            filename = save_profile_image(file, username)
            if filename:
                users[username]['profile_image'] = filename
                flash('Image de profil mise à jour avec succès')
    
    flash('Paramètres mis à jour avec succès')
    return redirect(url_for('settings'))

def check_ffmpeg():
    """Vérifie si ffmpeg est installé et accessible"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def sanitize_filename(filename):
    """Nettoie le nom de fichier en retirant les caractères problématiques"""
    # Remplacer les slashes et autres caractères problématiques par des tirets
    filename = re.sub(r'[/\\?%*:|"<>]', '-', filename)
    # Remplacer les espaces multiples par un seul espace
    filename = re.sub(r'\s+', ' ', filename)
    return filename.strip()

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
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch10'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch10:{query}", download=False)
            videos = []
            
            if 'entries' in results:
                for video in results['entries']:
                    if video:
                        # Récupérer la meilleure miniature disponible
                        thumbnail = None
                        if 'thumbnails' in video and video['thumbnails']:
                            # Prendre la dernière miniature (généralement la meilleure qualité)
                            thumbnail = video['thumbnails'][-1]['url']
                        elif 'thumbnail' in video:
                            thumbnail = video['thumbnail']
                            
                        videos.append({
                            'title': video.get('title', ''),
                            'url': f"https://www.youtube.com/watch?v={video.get('id', '')}",
                            'thumbnail': thumbnail,  # URL de la miniature
                            'duration': video.get('duration', 0),
                            'channel': video.get('channel', '')
                        })
            return videos
    except Exception as e:
        print(f"Erreur lors de la recherche : {str(e)}")
        return []

def get_video_info(url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info['title'],
                'channel': info.get('channel', 'Unknown Channel'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0)
            }
    except Exception as e:
        print(f"Erreur lors de la récupération des informations : {str(e)}")
        return None

def get_user_folder(user_id):
    """Crée et retourne le dossier de téléchargement spécifique à l'utilisateur"""
    user_folder = os.path.join(DOWNLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

@celery.task
def process_download(url, user_id):
    """Tâche Celery pour gérer le téléchargement en arrière-plan"""
    try:
        user_folder = get_user_folder(user_id)
        
        # Récupérer les informations de la vidéo
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'no_check_certificates': True,
            'prefer_insecure': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = f"{user_id}_{timestamp}"
            mp3_filename = f"{info['title']}_{unique_id}.mp3"
            mp3_path = os.path.join(user_folder, mp3_filename)
            
            # Télécharger la vidéo
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'outtmpl': os.path.join(user_folder, '%(title)s_' + unique_id + '.%(ext)s'),
                'no_check_certificates': True,
                'prefer_insecure': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            return {
                'success': True,
                'filename': mp3_filename,
                'title': info['title']
            }
    except Exception as e:
        return {'success': False, 'error': str(e)}

@celery.task
def cleanup_old_files():
    """Tâche Celery pour nettoyer les fichiers anciens"""
    try:
        current_time = datetime.now()
        for user_folder in os.listdir(DOWNLOAD_FOLDER):
            user_path = os.path.join(DOWNLOAD_FOLDER, user_folder)
            if os.path.isdir(user_path):
                for filename in os.listdir(user_path):
                    file_path = os.path.join(user_path, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    age_hours = (current_time - file_time).total_seconds() / 3600
                    
                    if age_hours > FILE_RETENTION_HOURS:
                        os.remove(file_path)
                
                # Supprimer le dossier utilisateur s'il est vide
                if not os.listdir(user_path):
                    os.rmdir(user_path)
    except Exception as e:
        print(f"Erreur lors du nettoyage : {str(e)}")

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = search_videos(query)
    return jsonify(results)

@app.route('/download')
@login_required
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'error': 'URL non fournie'}), 400
    
    # Vérifier le quota de l'utilisateur
    if not check_download_quota(current_user.id):
        return jsonify({'error': 'Vous avez atteint votre limite de téléchargements'}), 403
    
    try:
        # Définir les options pour la récupération des informations
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'  # Forcer la qualité à 320kbps
            }],
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info['title']
            filename = f"{title}.mp3"
            
            # Ajouter le log de téléchargement
            download_logs.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'username': current_user.id,
                'video_title': title,
                'video_url': video_url,
                'filename': filename
            })
            
            return jsonify({
                'success': True,
                'filename': filename,
                'title': title,
                'remaining_downloads': get_remaining_downloads(current_user.id)
            })
                
    except Exception as e:
        print(f"Erreur lors du téléchargement : {str(e)}")
        return jsonify({'error': f"Erreur lors du téléchargement : {str(e)}"}), 500

@app.route('/downloads/<path:filename>')
def get_file(filename):
    try:
        # Décoder le nom du fichier
        decoded_filename = urllib.parse.unquote(filename)
        # Ajouter l'extension .mp3 si elle n'est pas présente
        if not decoded_filename.endswith('.mp3'):
            decoded_filename += '.mp3'
            
        # Construire le chemin complet
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], decoded_filename)
        
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            app.logger.error(f"Fichier non trouvé: {file_path}")
            return "Fichier non trouvé", 404
            
        # Retourner le fichier
        return send_file(
            file_path,
            as_attachment=True,
            download_name=decoded_filename
        )
        
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération du fichier: {str(e)}")
        return "Erreur lors de la récupération du fichier", 500

def check_download_quota(user_id):
    """Vérifie si l'utilisateur a encore des téléchargements disponibles"""
    user = users.get(user_id)
    if not user:
        return False
    
    # Les administrateurs ont un quota illimité (0)
    if user['role'] == 'admin':
        return True
    
    # Compter les téléchargements de l'utilisateur dans les logs
    user_downloads = sum(1 for log in download_logs if log['username'] == user_id)
    
    return user_downloads < user['download_quota']

def get_remaining_downloads(user_id):
    """Retourne le nombre de téléchargements restants pour l'utilisateur"""
    user = users.get(user_id)
    if not user:
        return 0
    
    # Les administrateurs ont un quota illimité
    if user['role'] == 'admin':
        return "Illimité"
    
    # Compter les téléchargements de l'utilisateur dans les logs
    user_downloads = sum(1 for log in download_logs if log['username'] == user_id)
    
    return user['download_quota'] - user_downloads

# Ajouter cette fonction après la création de l'app Flask
@app.context_processor
def utility_processor():
    return {
        'get_remaining_downloads': get_remaining_downloads
    }

if __name__ == '__main__':
    if not check_ffmpeg():
        print("⚠️ FFmpeg n'est pas installé. Veuillez l'installer pour utiliser l'application.")
        sys.exit(1)
    app.run(debug=True)