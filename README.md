# YouTube MP3 Downloader

Une application web Flask permettant de télécharger des vidéos YouTube en format MP3 avec gestion des utilisateurs et des quotas de téléchargement.

## Fonctionnalités

- 🎵 Conversion des vidéos YouTube en MP3 haute qualité (320kbps)
- 🔍 Recherche de vidéos YouTube
- 👥 Système d'authentification avec rôles (admin/utilisateur)
- 📊 Gestion des quotas de téléchargement par utilisateur
- 👤 Profils utilisateurs personnalisables
- 📝 Journalisation des téléchargements
- 🧹 Nettoyage automatique des fichiers anciens
- 🎨 Interface utilisateur moderne et responsive
- 🔒 Sécurité renforcée avec validation des fichiers
- 📱 Compatible mobile et desktop

## Prérequis

- Python 3.8+
- FFmpeg
- Redis Server
- pip (gestionnaire de paquets Python)

## Installation

1. **Cloner le dépôt**
```bash
git clone <url-du-repo>
cd youtube-downloader
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Installer FFmpeg**

Sur Debian/Ubuntu :
```bash
sudo apt update
sudo apt install ffmpeg
```

Sur macOS avec Homebrew :
```bash
brew install ffmpeg
```

Sur Windows :
- Télécharger FFmpeg depuis [ffmpeg.org](https://ffmpeg.org/download.html)
- Ajouter le dossier bin à votre PATH système

5. **Installer et démarrer Redis**

Sur Debian/Ubuntu :
```bash
sudo apt install redis-server
sudo systemctl start redis
```

Sur macOS :
```bash
brew install redis
brew services start redis
```

Sur Windows :
- Télécharger Redis depuis [redis.io](https://redis.io/download)
- Suivre les instructions d'installation

## Configuration

1. **Créer les dossiers nécessaires**
```bash
mkdir downloads
mkdir static/uploads/profiles
```

2. **Démarrer Celery (dans un terminal séparé)**
```bash
celery -A app.celery worker --loglevel=info
```

3. **Démarrer Celery Beat (dans un terminal séparé)**
```bash
celery -A app.celery beat --loglevel=info
```

## Lancement de l'application

```bash
python app.py
```

L'application sera accessible à l'adresse : `http://localhost:5000`

## Comptes par défaut

- **Administrateur**
  - Utilisateur : admin
  - Mot de passe : admin123
  - Quota : Illimité
  - Accès : Toutes les fonctionnalités

> Note : Les utilisateurs standards devront être créés manuellement via l'interface d'administration.

## Structure du projet

```
youtube-downloader/
├── app.py                 # Application principale
├── requirements.txt       # Dépendances Python
├── downloads/            # Dossier des téléchargements
├── static/
│   ├── uploads/         # Dossier des images de profil
│   └── default-profile.png
└── templates/           # Templates HTML
    ├── admin.html       # Interface d'administration
    ├── index.html       # Page principale
    ├── login.html       # Page de connexion
    └── settings.html    # Page des paramètres
```

## Fonctionnalités administrateur

- Gestion des utilisateurs (création, modification, suppression)
- Configuration des quotas de téléchargement
- Consultation des logs de téléchargement
- Accès aux statistiques d'utilisation
- Gestion des profils utilisateurs

## Fonctionnalités utilisateur

- Recherche de vidéos YouTube
- Téléchargement en MP3 haute qualité
- Personnalisation du profil
- Suivi du quota de téléchargement
- Historique des téléchargements

## Sécurité

- Mots de passe hashés avec Werkzeug
- Protection contre les injections de fichiers
- Validation des extensions de fichiers
- Nettoyage automatique des fichiers temporaires
- Gestion des sessions sécurisée
- Protection CSRF

## Maintenance

- Les fichiers téléchargés sont automatiquement supprimés après 24 heures
- Nettoyage automatique des fichiers temporaires
- Journalisation des erreurs et des actions importantes
- Gestion des quotas par utilisateur

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Contacter l'administrateur

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) pour le téléchargement YouTube
- [Flask](https://flask.palletsprojects.com/) pour le framework web
- [Tailwind CSS](https://tailwindcss.com/) pour le design

## 📞 Support

Si vous rencontrez des problèmes ou avez des questions :
1. Vérifiez les [issues](https://github.com/SonikkProd/youtube-to-mp3/issues)
2. Créez une nouvelle issue si nécessaire
3. Assurez-vous d'avoir installé toutes les dépendances correctement

## 🔄 Mises à jour

Pour mettre à jour l'application :
```bash
git pull origin main
pip install -r requirements.txt
```

---

Fait avec ❤️ par SonikkProd
