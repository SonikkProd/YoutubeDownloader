# YouTube MP3 Downloader

Une application web Flask permettant de rechercher et télécharger des vidéos YouTube en format MP3 haute qualité (320kbps).

## 🚀 Fonctionnalités

- 🔍 Recherche de vidéos YouTube en temps réel
- ⬇️ Téléchargement en format MP3 haute qualité (320kbps)
- 👤 Système d'authentification utilisateur
- 🎨 Interface moderne et responsive
- 📱 Compatible mobile
- 🔄 Barre de progression pour les téléchargements
- ⌨️ Recherche via la touche Entrée
- 🎯 Gestion des erreurs et retours visuels

## 📋 Prérequis

- Python 3.8 ou supérieur
- FFmpeg
- pip (gestionnaire de paquets Python)

## 💻 Installation

1. **Cloner le repository**
```bash
git clone [URL_DU_REPO]
cd youtube-mp3-downloader
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel**
- Windows :
```bash
venv\Scripts\activate
```
- Linux/MacOS :
```bash
source venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Installer FFmpeg**
- Windows : Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html) et ajouter au PATH
- Linux : `sudo apt-get install ffmpeg`
- MacOS : `brew install ffmpeg`

## ⚙️ Configuration

1. **Créer un fichier `.env` à la racine du projet**
```env
SECRET_KEY=votre_clé_secrète
```

2. **Configurer les identifiants administrateur**
Modifier le fichier `config.py` avec vos identifiants souhaités.

## 🚀 Lancement

1. **Démarrer l'application**
```bash
python app.py
```

2. **Accéder à l'application**
Ouvrir un navigateur et aller à `http://localhost:5000`

## 📁 Structure du projet

```
youtube-to-mp3/
├── app.py              # Application Flask principale
├── requirements.txt    # Dépendances du projet
├── templates/         # Templates HTML
│   └── index.html     # Page principale
└── downloads/        # Dossier de téléchargement (créé automatiquement)
```

## ⚙️ Configuration

L'application utilise les paramètres suivants par défaut :
- Format audio : MP3
- Qualité : Meilleure qualité disponible
- Dossier de téléchargement : `downloads/`

## 🔒 Sécurité

- Les fichiers téléchargés sont stockés localement
- Aucune donnée n'est envoyée à des serveurs tiers
- Les fichiers sont supprimés automatiquement après le téléchargement

## ⚠️ Limitations

- Un seul téléchargement à la fois
- Les vidéos privées ne sont pas accessibles
- Certaines vidéos peuvent être protégées contre le téléchargement

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

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
