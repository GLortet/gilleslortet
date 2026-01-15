# gilleslortet.fr
Site professionnel de Gilles Lortet — formations PCM et Circuit Vital pour dirigeants, RH et HSE.

## Installation locale
Site professionnel de Gilles Lortet — Formation et accompagnement en fonctionnement humain (PCM & Circuit Vital).

## Stack
- Python (Flask)
- HTML / CSS
- Hébergement : PythonAnywhere

## Démarrage local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Le site est ensuite disponible sur `http://localhost:5000`.

## Structure du projet
```
.
├── app.py
├── requirements.txt
├── static
│   ├── app.js
│   ├── images
│   │   ├── hero.svg
│   │   └── portrait.svg
│   └── styles.css
├── templates
│   ├── a-propos.html
│   ├── approche.html
│   ├── base.html
│   ├── circuitvital.html
│   ├── contact.html
│   ├── home.html
│   └── pcm.html
└── README.md
```

## Checklist déploiement PythonAnywhere
- Créer une `virtualenv` et installer les dépendances : `pip install -r requirements.txt`.
- Configurer le fichier WSGI pour pointer vers `app` :
  ```python
  from app import app as application
  ```
- Vérifier que les fichiers statiques sont servis depuis `/static`.
- Recharger l'application depuis le tableau de bord PythonAnywhere (bouton “Reload”).
- Tester les routes principales : `/`, `/approche`, `/pcm`, `/circuitvital`, `/a-propos`, `/contact`.
