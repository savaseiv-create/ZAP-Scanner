# 🛡️ ZAP Scanner

Interface Web moderne et intuitive pour automatiser les scans de sécurité web via **OWASP ZAP (Zed Attack Proxy)**.


---

## ⚠️ Avertissement Légal & Éthique

> **Important** : Cet outil est conçu uniquement pour des tests de sécurité défensifs, des audits autorisés et des environnements de laboratoire. Le scan d'applications web sans autorisation explicite de leur propriétaire est illégal.
> Pour tester vos scans en toute sécurité, vous pouvez utiliser des plateformes d'entraînement dédiées comme [http://testphp.vulnweb.com](http://testphp.vulnweb.com).

---

## 🚀 Fonctionnalités

- 🕷️ **Spidering automatique** : Exploration des pages et des liens de l'application cible.
- ⚡ **Scan actif (Active Scan)** : Détection automatisée des vulnérabilités web (XSS, SQLi, CSRF, en-têtes manquants, etc.).
- 📊 **Tableau de bord interactif** : Suivi de la progression en temps réel et catégorisation des alertes par niveau de risque (*High, Medium, Low, Informational*).
- 📄 **Rapports téléchargeables** : Génération et téléchargement de rapports complets au format HTML.
- 🔒 **Gestion sécurisée des secrets** : Configuration via variables d'environnement (`.env`).

---

## 📋 Prérequis

1. **Python 3.8+** installé sur votre machine.
2. **OWASP ZAP** installé :
   - Téléchargement officiel : [https://www.zaproxy.org/download/](https://www.zaproxy.org/download/)

---

## ⚙️ Installation et Configuration

### 1. Cloner le dépôt
```bash
git clone https://github.com/savaseiv-create/ZAP-Scanner.git
cd ZapScanner
```

### 2. Créer un environnement virtuel (recommandé)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
Copiez le modèle `.env.example` vers un nouveau fichier `.env` :
```bash
# Windows (cmd)
copy .env.example .env

# Windows (PowerShell) / Linux / macOS
cp .env.example .env
```

Éditez le fichier `.env` pour y renseigner votre configuration :
```ini
ZAP_API_KEY=votre_cle_api_secrete
ZAP_HOST=127.0.0.1
ZAP_PORT=8080
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=False
```

---

## 🎮 Utilisation

### Étape 1 : Démarrer OWASP ZAP

#### Sous Windows :
Vous pouvez utiliser le script fourni [`start_zap.bat`]ou démarrer ZAP via votre terminal :
```cmd
start_zap.bat
```

#### En ligne de commande (tout OS) :
```bash
zap.sh -daemon -port 8080 -config api.key=votre_cle_api_secrete
```

Patientez environ 20 à 30 secondes pour que le moteur ZAP soit complètement initialisé.

---

### Étape 2 : Démarrer l'interface Web

```bash
python app.py
```

Ouvrez ensuite votre navigateur sur : **[http://localhost:5000](http://localhost:5000)**.

---

## 📁 Structure du Projet

```text
ZapScanner/
├── app.py              # Serveur Web Flask et API de pilotage
├── scanner.py          # Module d'interaction avec l'API OWASP ZAP
├── index.html          # Interface utilisateur moderne
├── start_zap.bat       # Script batch pour lancer ZAP en mode daemon (Windows)
├── reports/            # Dossier où sont enregistrés les rapports HTML
├── .env.example        # Modèle de variables d'environnement
├── .gitignore          # Exclusions Git (secrets, caches, rapports)
├── requirements.txt    # Dépendances Python
└── README.md           # Documentation
```

---



---

## 📄 Licence


