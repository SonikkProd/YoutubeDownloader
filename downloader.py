import os
import yt_dlp
import colorama
from colorama import Fore, Style
import subprocess
import sys

# Initialiser colorama pour les couleurs Windows
colorama.init()

def check_ffmpeg():
    """Vérifie si ffmpeg est installé et accessible"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def install_ffmpeg_guide():
    """Affiche les instructions pour installer ffmpeg"""
    print(f"\n{Fore.RED}❌ FFmpeg n'est pas installé sur votre système.{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}📝 Instructions d'installation de FFmpeg :{Style.RESET_ALL}")
    
    if sys.platform == 'win32':
        print(f"""
{Fore.CYAN}Méthode 1 (Recommandée) - Utiliser winget :{Style.RESET_ALL}
1. Ouvrez PowerShell en administrateur
2. Exécutez la commande : winget install ffmpeg

{Fore.CYAN}Méthode 2 - Installation manuelle :{Style.RESET_ALL}
1. Téléchargez FFmpeg depuis : https://www.gyan.dev/ffmpeg/builds/
2. Extrayez le fichier zip
3. Ajoutez le dossier bin à votre PATH système

{Fore.CYAN}Méthode 3 - Utiliser Chocolatey :{Style.RESET_ALL}
1. Installez Chocolatey si ce n'est pas déjà fait
2. Exécutez : choco install ffmpeg
""")
    elif sys.platform == 'darwin':
        print(f"""
{Fore.CYAN}Méthode 1 (Recommandée) - Utiliser Homebrew :{Style.RESET_ALL}
1. Ouvrez le Terminal
2. Exécutez : brew install ffmpeg
""")
    else:
        print(f"""
{Fore.CYAN}Pour Ubuntu/Debian :{Style.RESET_ALL}
sudo apt update && sudo apt install ffmpeg

{Fore.CYAN}Pour Fedora :{Style.RESET_ALL}
sudo dnf install ffmpeg

{Fore.CYAN}Pour Arch Linux :{Style.RESET_ALL}
sudo pacman -S ffmpeg
""")
    
    print(f"\n{Fore.YELLOW}Une fois FFmpeg installé, relancez ce script.{Style.RESET_ALL}")
    return False

def sanitize_filename(filename):
    # Remplacer les caractères non autorisés dans les noms de fichiers
    invalid_chars = '<>:"/\\|?*\n\r'
    # Nettoyer les espaces en début/fin de chaîne et les retours à la ligne
    filename = filename.strip()
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Supprimer les underscores multiples
    while '__' in filename:
        filename = filename.replace('__', '_')
    return filename

def download_youtube_mp3(url):
    try:
        # Créer le dossier de téléchargement s'il n'existe pas
        download_folder = "downloads"
        os.makedirs(download_folder, exist_ok=True)
        
        print(f"\n{Fore.CYAN}🎵 Récupération des informations de la vidéo...{Style.RESET_ALL}")
        
        # Options pour yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Qualité maximale en kbps
                'nopostoverwrites': False,  # Permet de réécrire si meilleure qualité
            }],
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'no_check_certificates': True,
            'prefer_insecure': True,
            'format_sort': ['abr:320'],  # Préférer les formats avec un bitrate de 320kbps
            'postprocessor_args': [
                '-codec:a', 'libmp3lame',  # Utiliser LAME pour une meilleure qualité
                '-q:a', '0',  # Qualité maximale pour LAME
                '-b:a', '320k',  # Force le bitrate à 320k
            ],
        }
        
        # Télécharger et convertir en MP3
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Récupérer les informations de la vidéo
                info = ydl.extract_info(url, download=False)
                
                # Vérifier si la vidéo est disponible
                if info is None:
                    print(f"\n{Fore.RED}❌ La vidéo n'est pas disponible ou est privée.{Style.RESET_ALL}")
                    return
                
                # Afficher les informations
                print(f"\n{Fore.YELLOW}📺 Titre : {info['title']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}👤 Chaîne : {info['channel']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}⏱️ Durée : {info['duration']} secondes{Style.RESET_ALL}")
                
                # Télécharger la vidéo
                print(f"\n{Fore.CYAN}⬇️ Téléchargement et conversion en MP3...{Style.RESET_ALL}")
                ydl.download([url])
                
                # Construire le chemin du fichier MP3
                clean_title = sanitize_filename(info['title'])
                mp3_path = os.path.join(download_folder, f"{clean_title}.mp3")
                
                print(f"\n{Fore.GREEN}✨ Téléchargement terminé !{Style.RESET_ALL}")
                print(f"{Fore.CYAN}📁 Fichier sauvegardé : {mp3_path}{Style.RESET_ALL}")
                
            except yt_dlp.utils.DownloadError as e:
                print(f"\n{Fore.RED}❌ Erreur de téléchargement : {str(e)}{Style.RESET_ALL}")
                if "ffmpeg not found" in str(e):
                    install_ffmpeg_guide()
                else:
                    print(f"{Fore.YELLOW}💡 Conseil : Vérifiez que la vidéo n'est pas privée ou supprimée.{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}❌ Erreur inattendue : {str(e)}{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erreur : {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Conseil : Vérifiez votre connexion internet et l'URL de la vidéo.{Style.RESET_ALL}")

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            # Calculer le pourcentage
            if 'total_bytes' in d and 'downloaded_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                print(f"\r{Fore.CYAN}⬇️ Téléchargement : {percent:.1f}%{Style.RESET_ALL}", end='')
            elif 'downloaded_bytes' in d:
                # Si on n'a pas la taille totale, afficher juste les Mo téléchargés
                mb_downloaded = d['downloaded_bytes'] / 1024 / 1024
                print(f"\r{Fore.CYAN}⬇️ Téléchargé : {mb_downloaded:.1f} Mo{Style.RESET_ALL}", end='')
        except:
            # En cas d'erreur dans l'affichage de la progression, ne rien faire
            pass
    elif d['status'] == 'finished':
        print(f"\n{Fore.CYAN}🔄 Conversion en MP3...{Style.RESET_ALL}")

def main():
    print(f"{Fore.CYAN}=== YouTube MP3 Downloader ==={Style.RESET_ALL}")
    
    # Vérifier si ffmpeg est installé
    if not check_ffmpeg():
        install_ffmpeg_guide()
        return
    
    # Mettre à jour yt-dlp au démarrage
    print(f"\n{Fore.CYAN}🔄 Mise à jour de yt-dlp...{Style.RESET_ALL}")
    os.system('pip install --upgrade yt-dlp')
    
    while True:
        url = input(f"\n{Fore.YELLOW}Entrez l'URL YouTube (ou 'q' pour quitter) : {Style.RESET_ALL}").strip()
        
        if url.lower() == 'q':
            print(f"\n{Fore.GREEN}👋 Au revoir !{Style.RESET_ALL}")
            break
            
        if "youtube.com" in url or "youtu.be" in url:
            download_youtube_mp3(url)
        else:
            print(f"\n{Fore.RED}❌ URL YouTube invalide !{Style.RESET_ALL}")

if __name__ == "__main__":
    main()