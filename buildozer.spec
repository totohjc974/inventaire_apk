[app]

# Titre de l'application (apparaît sous l'icône)
title = Gestion Inventaire

# Nom du package (doit être unique)
package.name = inventorymanager

# Domaine du package (inverse de votre site web)
package.domain = com.yourcompany

# Code source principal
source.dir = .

# Fichiers à inclure
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf

# Point d'entrée principal
source.main = main.py

# Version de l'application (format: major.minor.revision)
version = 1.0.0

# Requirements (DÉPENDANCES - TRÈS IMPORTANT!)
requirements = 
    python3,
    kivy==2.1.0,
    opencv-python-headless==4.5.5.64,
    numpy==1.21.6,
    pyzbar==0.1.9,
    android,
    pillow==9.0.1

# Permissions Android
android.permissions = 
    CAMERA,
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    VIBRATE

# Fonctionnalités Android
android.features = 
    camera

# Configuration Android
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.ndk_api = 21

# Architectures (armeabi-v7a est compatible avec la plupart des appareils)
android.arch = armeabi-v7a

# Orientation de l'écran
orientation = portrait

# Plein écran
fullscreen = 0

# Empêcher l'écran de s'éteindre
android.wakelock = 1

# Configuration de la fenêtre
window.resizeable = 0

# Type d'application
# android.meta_data = 
# android.intent_filters =

# Icones de l'application
# icon.filename = %(source.dir)s/data/icon.png
# Créez un dossier 'data' et placez-y vos icônes:
# icon-36.png, icon-48.png, icon-72.png, icon-96.png, icon-144.png

# Écran de démarrage (presplash)
# presplash.filename = %(source.dir)s/data/presplash.png
# presplash.color = #FFFFFF

# Règles de presse-papier
android.allow_backup = True

# Services et activités
android.entrypoint = org.kivy.android.PythonActivity

# Règles de packaging
android.accept_sdk_license = True
android.ignore_path_patterns = 
    .git,
    __pycache__,
    *.pyc,
    .buildozer,
    bin,
    tests,
    venv,
    *.iml,
    .idea

# Activer le support de la caméra
android.uses_camera = 1

# Bibliothèques spécifiques pour OpenCV et pyzbar
android.add_libs_armeabi_v7a = 
    libs/armeabi-v7a/libopencv_java4.so,
    libs/armeabi-v7a/libzbar.so

# Règles de logging
log_level = 2

# Configuration pour la compilation (release/debug)
# (commenté par défaut - décommentez pour release)

#[app:release]
# Décommentez et remplacez par votre clé de signature
#android.release_artifact = .apk
#android.keyalias = 
#android.keyalias_passwd = 
#android.keystore = 
#android.keystore_passwd = 

# Commandes de build personnalisées
#
# build.gradle
# gradle.buildozer.gradle = gradle.buildozer.gradle
#
# Commande de pré-compilation
# prebuild.command = 
#
# Commande de post-compilation
# postbuild.command = 

# Hook personnalisé pour copier les bibliothèques OpenCV
# (Décommentez si vous avez des fichiers .so à copier)
# prebuild.command = 
#    mkdir -p libs/armeabi-v7a &&
#    cp -r /chemin/vers/vos/libs/* libs/armeabi-v7a/ || true

# Options de build
[buildozer]

# Dossier de sortie
# build_dir = .buildozer

# Dossier de destination
# bin_dir = ./bin

# Journalisation
log_level = 2

# Nettoyer le build
warn_on_root = 1

# Configuration pour différents profils
[app:demo]
title = Gestion Inventaire (Demo)
package.name = inventorymanagerdemo
package.domain = com.yourcompany.demo

[app:pro]
title = Gestion Inventaire Pro
package.name = inventorymanagerpro
package.domain = com.yourcompany.pro
#android.allow_backup = False