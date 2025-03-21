# YouTube MP3 Downloader

Une application web simple et élégante pour télécharger des musiques YouTube en format MP3. Cette application permet de rechercher et télécharger facilement vos musiques préférées avec une interface utilisateur intuitive.

## 🎯 Fonctionnalités

- 🔍 Recherche de vidéos YouTube par titre ou URL
- 🎵 Téléchargement en MP3 de haute qualité
- 🖼️ Affichage des miniatures des vidéos
- 📱 Interface responsive et moderne
- ⚡ Téléchargement rapide et efficace
- 🎨 Interface utilisateur intuitive

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- FFmpeg (pour la conversion audio)

## 🛠️ Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/SonikkProd/youtube-to-mp3.git
cd youtube-to-mp3
```

2. Installez FFmpeg :
   - **Windows** : Téléchargez FFmpeg depuis [le site officiel](https://ffmpeg.org/download.html) et ajoutez-le à votre PATH
   - **Linux** : `sudo apt-get install ffmpeg`
   - **macOS** : `brew install ffmpeg`

3. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

4. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

1. Démarrez l'application :
```bash
python app.py
```

2. Ouvrez votre navigateur et accédez à :
```
http://localhost:5000
```

3. Utilisez l'application :
   - Entrez le titre de la musique ou l'URL YouTube dans la barre de recherche
   - Cliquez sur "Rechercher" ou appuyez sur Entrée
   - Sélectionnez la vidéo souhaitée parmi les résultats
   - Cliquez sur "Télécharger" pour obtenir le fichier MP3

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
