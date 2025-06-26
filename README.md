# 📚 Système de Gestion des Absences – BTS

Application de bureau moderne développée avec **PyQt5** et **MySQL** pour la gestion numérique des absences des étudiants en BTS. Ce projet a été réalisé dans le cadre d’un mini-projet de fin de module pour le BTS-DIA 2024/2025 au Lycée Technique MED_V.

## ✨ Fonctionnalités

- 🔐 Connexion sécurisée à la base de données
- 👨‍🎓 Gestion des étudiants (ajout, modification, suppression, affichage)
- 📆 Enregistrement et suivi des absences avec statut (justifié / non justifié)
- 📊 Statistiques dynamiques :
  - Total et répartition des absences
  - Taux moyen par classe
  - Top 5 des étudiants les plus absents
- 📤 Export CSV des données
- 📧 Envoi de rapports par e-mail (configuration SMTP intégrée)
- 🧠 Sauvegarde automatique des données (backup SQL)
- 🎨 Interface utilisateur moderne avec thèmes stylisés

## 🛠️ Technologies utilisées

- Python 3.x
- PyQt5 (interface graphique)
- MySQL + mysql-connector-python
- smtplib / email.mime (envoi d’emails)
- csv (export des données)
- configparser (fichiers de configuration)
- datetime / os / sys

---

## 📦 Modules à installer

Avant de lancer l'application, vous devez installer les modules suivants :

Modules utilisés dans le projet :

PyQt5

mysql-connector-python

smtplib (inclus dans Python)

email.mime (inclus dans Python)

csv (inclus dans Python)

configparser (inclus dans Python)

datetime, os, sys (inclus dans Python)

🔧 Installation
Cloner le dépôt :
git clone https://github.com/hamzapy-eng/gestion-absences-bts.git
cd gestion-absences-bts

Installer les dépendances :
Vous devez installer les modules suivants:
   pip install PyQt5 mysql-connector-python

Configurer la base de données :
   Créer une base de données nommée gestion_absences_BTS dans MySQL.
   Les tables sont créées automatiquement à la première connexion.

Lancer l'application :
bash
python prject_abcence_bts.py

📁 Structure
scss
📦gestion-absences-bts
 ┣ 📄 prject_abcence_bts.py
 ┣ 📄 README.md
 ┣ 📄 email_config.ini (généré automatiquement)
 ┣ 📄 app_config.ini (sauvegarde de session)
 ┗ 📁 backups (sauvegardes SQL auto)
💡 À propos du projet
Ce projet a été réalisé par Hamza Dine et Soufian Amzil
dans le cadre du module développement au BTS-DIA 2024/2025
Lycée Technique MED_V

🚀 Perspectives futures
Intégration d’une IA pour détecter les absences suspectes

Tableau de bord dynamique avec graphiques

Système multi-utilisateur avec rôles et permissions

