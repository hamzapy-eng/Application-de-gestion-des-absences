# ------ Modules pour l'interface graphique avec PyQt5 -------
from PyQt5.QtCore import QDate, Qt, QTimer                  # Gestion des dates, constantes Qt et minuteur (auto-sauvegarde)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont       # Gestion des icônes, images, couleurs, polices
from PyQt5.QtWidgets import (                               
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QTabWidget, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QDateEdit, QFormLayout,
    QFileDialog, QTextEdit, QStatusBar, QDialog, QDialogButtonBox,
    QGroupBox, QMainWindow, QAction, QToolBar, QSystemTrayIcon
)  # Composants principaux pour construire l'interface utilisateur

# ------- Connexion à la base de données MySQL -------
import mysql.connector                 # Connexion à MySQL
from mysql.connector import Error     # Gestion des erreurs MySQL

# -------- Gestion de l'application --------
import sys                            # Utilisé pour gérer les arguments de la ligne de commande et quitter l'application

# ------- Création et gestion de fichiers CSV -------
import csv                            # Pour exporter les données vers des fichiers CSV

# ------- Envoi d'emails -------
from email.mime.text import MIMEText          # Pour créer une partie texte simple dans un email
from email.mime.multipart import MIMEMultipart  # Pour créer un email avec plusieurs parties (texte, HTML, pièces jointes)
import smtplib                                # 
# ------- Fichier de configuration -------
import configparser                  # Pour lire/écrire des fichiers INI contenant les paramètres (ex: email, SMTP, etc.)
# ------- Gestion du système de fichiers -------
import os                            # Pour interagir avec le système (fichiers, dossiers, chemins)

# ------- Dates et heures -------
from datetime import datetime        # Pour récupérer ou formater la date et l'heure actuelles


class EmailSender(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Send Absence Report via Email")  # Titre de la fenêtre de dialogue
        self.setWindowIcon(parent.windowIcon())  # Utilise l'icône de la fenêtre principale
        self.setModal(True)  # Bloque les interactions avec la fenêtre principale tant que ce dialogue est ouvert
        self.resize(600, 400)  # Taille de la fenêtre

        layout = QVBoxLayout()  # Layout vertical principal

        # ----- Section configuration email -----
        config_group = QGroupBox("Email Configuration")  # Groupe de champs pour configurer l'envoi d'email
        config_layout = QFormLayout()  # Formulaire vertical (étiquette + champ)

        # Champs pour les informations de l'expéditeur
        self.sender_email = QLineEdit()  # Email de l’expéditeur
        self.sender_password = QLineEdit()  # Mot de passe (sera masqué)
        self.sender_password.setEchoMode(QLineEdit.Password)  # Cache les caractères saisis
        self.smtp_server = QLineEdit("smtp.gmail.com")  # Serveur SMTP par défaut
        self.smtp_port = QLineEdit("587")  # Port SMTP par défaut

        # Ajout des champs dans le layout
        config_layout.addRow(QLabel("Sender Email:"), self.sender_email)
        config_layout.addRow(QLabel("Password:"), self.sender_password)
        config_layout.addRow(QLabel("SMTP Server:"), self.smtp_server)
        config_layout.addRow(QLabel("SMTP Port:"), self.smtp_port)
        config_group.setLayout(config_layout)  # Appliquer le layout au groupe

        # ----- Section contenu email -----
        content_group = QGroupBox("Email Content")  # Groupe de contenu de l’email
        content_layout = QVBoxLayout()  # Layout vertical

        # Destinataire
        self.recipient_label = QLabel("Recipient Email:")
        self.recipient_input = QLineEdit()

        # Sujet
        self.subject_label = QLabel("Subject:")
        self.subject_input = QLineEdit("Absence Report")  # Sujet par défaut

        # Message
        self.message_label = QLabel("Message:")
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter your message here.")  # Aide dans le champ

        # Ajouter les champs dans le layout
        content_layout.addWidget(self.recipient_label)
        content_layout.addWidget(self.recipient_input)
        content_layout.addWidget(self.subject_label)
        content_layout.addWidget(self.subject_input)
        content_layout.addWidget(self.message_label)
        content_layout.addWidget(self.message_input)
        content_group.setLayout(content_layout)

        # ----- Boutons OK/Annuler -----
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # Crée boutons standards
        button_box.accepted.connect(self.send_email)  # Lien bouton OK à la fonction d'envoi
        button_box.rejected.connect(self.reject)  # Lien bouton Annuler à la fermeture de la fenêtre

        # Changer le texte du bouton OK
        self.send_button = button_box.button(QDialogButtonBox.Ok)
        self.send_button.setText("Send Email")

        # Charger une ancienne configuration si disponible
        self.load_config()

        # Ajouter les groupes et les boutons dans le layout principal
        layout.addWidget(config_group)
        layout.addWidget(content_group)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def load_config(self):
        """Charge les paramètres SMTP sauvegardés précédemment depuis email_config.ini"""
        config = configparser.ConfigParser()
        if os.path.exists('email_config.ini'): #fichier qui contient l'email et le password generer par google
            config.read('email_config.ini')
            if 'EMAIL' in config:
                self.sender_email.setText(config['EMAIL'].get('sender', ''))
                self.sender_password.setText(config['EMAIL'].get('password', ''))
                self.smtp_server.setText(config['EMAIL'].get('server', 'smtp.gmail.com'))
                self.smtp_port.setText(config['EMAIL'].get('port', '587'))
                

    def save_config(self):
        """Sauvegarde les paramètres de configuration dans email_config.ini """
        config = configparser.ConfigParser()
        config['EMAIL'] = {
            'sender': self.sender_email.text(),
            'password': self.sender_password.text(),
            'server': self.smtp_server.text(),
            'port': self.smtp_port.text()
        }
        with open('email_config.ini', 'w') as configfile:
            config.write(configfile)

    def send_email(self):
        """Fonction qui prépare et envoie l'email via SMTP"""
        # Récupération des données du formulaire
        sender_email = self.sender_email.text().strip()
        sender_password = self.sender_password.text().strip()
        recipient = self.recipient_input.text().strip()
        subject = self.subject_input.text().strip()
        message_body = self.message_input.toPlainText().strip()
        smtp_server = self.smtp_server.text().strip()
        smtp_port = self.smtp_port.text().strip()

        # Vérification des champs obligatoires
        if not all([sender_email, recipient, subject]):
            QMessageBox.warning(self, "Missing Fields", "Please fill all required fields before sending.")
            return

        try:
            msg = MIMEMultipart()  # Crée un email multi-parties
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject

            # Ajoute le message texte
            msg.attach(MIMEText(message_body, "plain"))

            # Ajoute la date d'envoi dans le pied du message
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer = f"\n\nThis email was sent from Absence Management System on {current_date}"
            msg.attach(MIMEText(message_body + footer, "plain"))

            # Sauvegarde la configuration 
            self.save_config()

            try:
                # Connexion et envoi de l’email via SMTP
                server = smtplib.SMTP(smtp_server, int(smtp_port))
                server.starttls()  # Sécurise la connexion
                server.login(sender_email, sender_password)  # Connexion au serveur SMTP
                server.send_message(msg)  # Envoi du message
                server.quit()

                QMessageBox.information(self, "Success", "Email sent successfully!")
                self.accept()  # Ferme la boîte de dialogue
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send email:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to prepare email:\n{str(e)}")


class AbsenceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_styles()
        self.create_menu()
        self.create_toolbar()
        self.setup_icon()
        
        # Database connection
        self.db_connection = None
        self.cursor = None
        
        
        # Load last session
        self.load_last_session()
        
    def setup_ui(self):
        """Initialize the main UI components"""
        self.setWindowTitle("Gestion Absences BTS")
        self.setGeometry(0, 0, 1922, 1035)
        self.setWindowIcon(QIcon("logolycee.png"))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_connection_tab(), "Connexion")
        self.tabs.addTab(self.create_students_tab(), "Étudiants")
        self.tabs.addTab(self.create_absences_tab(), "Absences")
        self.tabs.addTab(self.create_Statistiques_tab(), "Statistiques")
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
    
    def create_menu(self):
        """Create the main menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Fichier")
        
        export_action = QAction("Exporter données", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Outils")
        
        email_action = QAction("Envoyer email", self)
        email_action.triggered.connect(self.open_email_dialog)
        tools_menu.addAction(email_action)
        
        settings_action = QAction("Paramètres", self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("Aide")
        
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
    def setup_icon(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.icon = QSystemTrayIcon(self)
        self.icon.setIcon(QIcon("logolycee.png"))
        
    def create_connection_tab(self):
        """Create the database connection tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Connection form
        form_group = QGroupBox("Paramètres de connexion")
        form_layout = QVBoxLayout()
        
        self.host_input = QLineEdit("localhost")
        self.user_input = QLineEdit("root")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.db_input = QLineEdit("gestion_absences_BTS")
        
        form_layout.addWidget(QLabel("Serveur:"))
        form_layout.addWidget(self.host_input)
        form_layout.addWidget(QLabel("Utilisateur:"))
        form_layout.addWidget(self.user_input)
        form_layout.addWidget(QLabel("Mot de passe:"))
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(QLabel("Base de données:"))
        form_layout.addWidget(self.db_input)
        form_group.setLayout(form_layout)

        # Connection buttons
        btn_layout = QHBoxLayout()
        connect_btn = QPushButton("Se connecter")
        connect_btn.clicked.connect(self.connect_db)
        disconnect_btn = QPushButton("Se déconnecter")
        disconnect_btn.clicked.connect(self.disconnect_db)
        
        btn_layout.addWidget(connect_btn)
        btn_layout.addWidget(disconnect_btn)
        
        # Logo
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("logolycee.png").scaled(200, 200, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(logo_label)
        layout.addWidget(form_group)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_students_tab(self):
        """Create the students management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Student form
        form_group = QGroupBox("Ajouter un étudiant")
        form_layout = QFormLayout()
        
        self.student_code_massar = QLineEdit()
        self.student_name = QLineEdit()
        self.student_prenom = QLineEdit()
        self.student_cin = QLineEdit()
        self.student_class = QComboBox()
        self.student_class.addItems(["BTS1", "BTS2"])
        
        form_layout.addRow(QLabel("Code Massar:"), self.student_code_massar)
        form_layout.addRow(QLabel("Nom:"), self.student_name)
        form_layout.addRow(QLabel("Prénom:"), self.student_prenom)
        form_layout.addRow(QLabel("CIN:"), self.student_cin)
        form_layout.addRow(QLabel("Classe:"), self.student_class)
        form_group.setLayout(form_layout)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Ajouter étudiant")
        add_btn.clicked.connect(self.add_student)
        update_btn = QPushButton("Modifier")
        update_btn.clicked.connect(self.update_student)
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self.delete_student)
        view_btn = QPushButton("Actualiser")
        view_btn.clicked.connect(self.view_students)
        export_btn = QPushButton("Exporter CSV")
        export_btn.clicked.connect(self.export_students_csv)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(update_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(view_btn)
        btn_layout.addWidget(export_btn)
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(["Code Massar", "CIN", "Nom", "Prénom", "Classe"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.students_table.setSelectionMode(QTableWidget.SingleSelection)
        self.students_table.cellClicked.connect(self.student_table_clicked)
        
        layout.addWidget(form_group)
        layout.addLayout(btn_layout)
        layout.addWidget(self.students_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_absences_tab(self):
        """Create the absences management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Absence form
        form_group = QGroupBox("Enregistrer une absence")
        form_layout = QFormLayout()
        
        self.absence_student = QComboBox()
        self.absence_date = QDateEdit()
        self.absence_date.setDisplayFormat("yyyy-MM-dd")
        self.absence_date.setDate(QDate.currentDate())
        self.absence_reason = QComboBox()
        self.absence_reason.addItems(["Maladie", "Famille", "Personnel", "Transport", "Autre"])
        self.absence_status = QComboBox()
        self.absence_status.addItems(["Justifie", "Non justifie"])
        self.absence_notes = QLineEdit()
        self.absence_notes.setPlaceholderText("Notes supplémentaires...")
        
        form_layout.addRow(QLabel("Étudiant:"), self.absence_student)
        form_layout.addRow(QLabel("Date:"), self.absence_date)
        form_layout.addRow(QLabel("Raison:"), self.absence_reason)
        form_layout.addRow(QLabel("Statut:"), self.absence_status)
        form_layout.addRow(QLabel("Notes:"), self.absence_notes)
        form_group.setLayout(form_layout)
        
        # Filter controls
        filter_group = QGroupBox("Filtrer les absences")
        filter_layout = QHBoxLayout()
        
        self.filter_class = QComboBox()
        self.filter_class.addItems(["Toutes", "BTS1", "BTS2"])
        self.filter_status = QComboBox()
        self.filter_status.addItems(["Tous", "Justifié", "Non justifié"])
        self.filter_date_from = QDateEdit()
        self.filter_date_from.setDisplayFormat("yyyy-MM-dd")
        self.filter_date_from.setDate(QDate.currentDate().addMonths(-1))
        self.filter_date_to = QDateEdit()
        self.filter_date_to.setDisplayFormat("yyyy-MM-dd")
        self.filter_date_to.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel("Classe:"))
        filter_layout.addWidget(self.filter_class)
        filter_layout.addWidget(QLabel("Statut:"))
        filter_layout.addWidget(self.filter_status)
        filter_layout.addWidget(QLabel("De:"))
        filter_layout.addWidget(self.filter_date_from)
        filter_layout.addWidget(QLabel("À:"))
        filter_layout.addWidget(self.filter_date_to)
        
        filter_btn = QPushButton("Filtrer")
        filter_btn.clicked.connect(self.view_absences)
        filter_layout.addWidget(filter_btn)
        
        filter_group.setLayout(filter_layout)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Enregistrer")
        add_btn.clicked.connect(self.add_absence)
        update_btn = QPushButton("Modifier")
        update_btn.clicked.connect(self.update_absence)
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(self.delete_absence)
        view_btn = QPushButton("Actualiser")
        view_btn.clicked.connect(self.view_absences)
        export_btn = QPushButton("Exporter CSV")
        export_btn.clicked.connect(self.export_absences_csv)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(update_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(view_btn)
        btn_layout.addWidget(export_btn)
        
        # Absences table
        self.absences_table = QTableWidget()
        self.absences_table.setColumnCount(7)
        self.absences_table.setHorizontalHeaderLabels(["ID", "Code Massar", "Nom", "Date", "Raison", "Statut", "Notes"])
        self.absences_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.absences_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.absences_table.setSelectionMode(QTableWidget.SingleSelection)
        self.absences_table.cellClicked.connect(self.absence_table_clicked)
        
        layout.addWidget(form_group)
        layout.addWidget(filter_group)
        layout.addLayout(btn_layout)
        layout.addWidget(self.absences_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_Statistiques_tab(self):
        """Create the statistics tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Statistics controls
        stats_group = QGroupBox("Statistiques des absences")
        stats_layout = QHBoxLayout()
        
        self.stats_class = QComboBox()
        self.stats_class.addItems(["Toutes", "BTS1", "BTS2"])
        self.stats_period = QComboBox()
        self.stats_period.addItems(["7 derniers jours", "30 derniers jours", "Ce mois", "Ce semestre", "Personnalisé"])
        self.stats_date_from = QDateEdit()
        self.stats_date_from.setDisplayFormat("yyyy-MM-dd")
        self.stats_date_from.setDate(QDate.currentDate().addMonths(-1))
        self.stats_date_to = QDateEdit()
        self.stats_date_to.setDisplayFormat("yyyy-MM-dd")
        self.stats_date_to.setDate(QDate.currentDate())
        
        stats_layout.addWidget(QLabel("Classe:"))
        stats_layout.addWidget(self.stats_class)
        stats_layout.addWidget(QLabel("Période:"))
        stats_layout.addWidget(self.stats_period)
        stats_layout.addWidget(QLabel("De:"))
        stats_layout.addWidget(self.stats_date_from)
        stats_layout.addWidget(QLabel("À:"))
        stats_layout.addWidget(self.stats_date_to)
        
        generate_btn = QPushButton("Générer")
        generate_btn.clicked.connect(self.generate_stats)
        stats_layout.addWidget(generate_btn)
        
        stats_group.setLayout(stats_layout)
        
        # Statistics display
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        
        layout.addWidget(stats_group)
        layout.addWidget(self.stats_display)
        
        tab.setLayout(layout)
        return tab
    
    def connect_db(self):
        """Connect to the database"""
        try:
            self.db_connection = mysql.connector.connect(
                host=self.host_input.text(),
                user=self.user_input.text(),
                password=self.password_input.text(),
                database=self.db_input.text()
            )
            self.cursor = self.db_connection.cursor(dictionary=True)
            self.create_tables()
            self.load_students()
            self.view_students()
            self.view_absences()
            self.update_status("Connecté à la base de données")
            
            # Enable tabs after successful connection
            for i in range(1, self.tabs.count()):
                self.tabs.setTabEnabled(i, True)
                
            QMessageBox.information(self, "Succès", "Connexion réussie!")
        except Error as e:
            self.update_status("Échec de connexion")
            QMessageBox.critical(self, "Erreur", f"Échec de connexion: {str(e)}")
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS etudiants (
                    code_massar VARCHAR(50) PRIMARY KEY,
                    cin VARCHAR(50),
                    nom VARCHAR(100) NOT NULL,
                    prenom VARCHAR(100) NOT NULL,
                    classe VARCHAR(20) NOT NULL,
                    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS absences (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    code_massar VARCHAR(50) NOT NULL,
                    date_absence DATE NOT NULL,
                    raison VARCHAR(100) NOT NULL,
                    statut VARCHAR(20) NOT NULL,
                    notes TEXT,
                    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (code_massar) REFERENCES etudiants(code_massar)
                    ON DELETE CASCADE
                )
            """)
            self.db_connection.commit()
            self.update_status("Tables créées avec succès")
        except Error as e:
            self.update_status("Erreur création tables")
            QMessageBox.critical(self, "Erreur", f"Échec création tables: {str(e)}")
    
    def disconnect_db(self):
        """Disconnect from the database"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.db_connection and self.db_connection.is_connected():
                self.db_connection.close()
            self.update_status("Déconnecté de la base de données")
            
            # Disable tabs after disconnection
            for i in range(1, self.tabs.count()):
                self.tabs.setTabEnabled(i, False)
                
            QMessageBox.information(self, "Info", "Déconnecté de la base de données")
        except Error as e:
            self.update_status("Erreur de déconnexion")
            QMessageBox.critical(self, "Erreur", f"Erreur de déconnexion: {str(e)}")
    
    def add_student(self):
        """Add a new student to the database"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        code_massar = self.student_code_massar.text().strip()
        nom = self.student_name.text().strip()
        prenom = self.student_prenom.text().strip()
        cin = self.student_cin.text().strip()
        classe = self.student_class.currentText()
        
        if not nom or not prenom or not classe:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs obligatoires")
            return
            
        if not code_massar:
            code_massar = f"{nom[:3]}{prenom[:3]}{cin[-4:]}" if cin else f"{nom[:3]}{prenom[:3]}"
            
        try:
            self.cursor.execute(
                "INSERT INTO etudiants (code_massar, cin, nom, prenom, classe) VALUES (%s, %s, %s, %s, %s)",
                (code_massar, cin, nom, prenom, classe)
            )
            self.db_connection.commit()
            self.update_status(f"Étudiant {nom} {prenom} ajouté avec succès")
            QMessageBox.information(self, "Succès", "Étudiant ajouté avec succès!")
            self.clear_student_form()
            self.load_students()
            self.view_students()
        except Error as e:
            self.update_status("Erreur d'ajout étudiant")
            QMessageBox.critical(self, "Erreur", f"Échec d'ajout: {str(e)}")
    
    def update_student(self):
        """Update an existing student"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        selected_row = self.students_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un étudiant à modifier")
            return
            
        old_code = self.students_table.item(selected_row, 0).text()
        new_code = self.student_code_massar.text().strip()
        nom = self.student_name.text().strip()
        prenom = self.student_prenom.text().strip()
        cin = self.student_cin.text().strip()
        classe = self.student_class.currentText()
        
        if not nom or not prenom or not classe:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs obligatoires")
            return
            
        try:
            self.cursor.execute(
                "UPDATE etudiants SET code_massar=%s, cin=%s, nom=%s, prenom=%s, classe=%s WHERE code_massar=%s",
                (new_code, cin, nom, prenom, classe, old_code)
            )
            self.db_connection.commit()
            self.update_status(f"Étudiant {nom} {prenom} mis à jour")
            QMessageBox.information(self, "Succès", "Étudiant mis à jour avec succès!")
            self.clear_student_form()
            self.load_students()
            self.view_students()
        except Error as e:
            self.update_status("Erreur de mise à jour étudiant")
            QMessageBox.critical(self, "Erreur", f"Échec de mise à jour: {str(e)}")
    
    def delete_student(self):
        """Delete a student from the database"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        selected_row = self.students_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un étudiant à supprimer")
            return
            
        code_massar = self.students_table.item(selected_row, 0).text()
        nom = self.students_table.item(selected_row, 2).text()
        prenom = self.students_table.item(selected_row, 3).text()
        
        reply = QMessageBox.question(
            self, "Confirmation", 
            f"Voulez-vous vraiment supprimer l'étudiant {nom} {prenom}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM etudiants WHERE code_massar=%s", (code_massar,))
                self.db_connection.commit()
                self.update_status(f"Étudiant {nom} {prenom} supprimé")
                QMessageBox.information(self, "Succès", "Étudiant supprimé avec succès!")
                self.clear_student_form()
                self.load_students()
                self.view_students()
            except Error as e:
                self.update_status("Erreur de suppression étudiant")
                QMessageBox.critical(self, "Erreur", f"Échec de suppression: {str(e)}")
    
    def student_table_clicked(self, row, column):
        """Load student data into form when clicked in table"""
        code_massar = self.students_table.item(row, 0).text()
        cin = self.students_table.item(row, 1).text()
        nom = self.students_table.item(row, 2).text()
        prenom = self.students_table.item(row, 3).text()
        classe = self.students_table.item(row, 4).text()
        
        self.student_code_massar.setText(code_massar)
        self.student_name.setText(nom)
        self.student_prenom.setText(prenom)
        self.student_cin.setText(cin)
        self.student_class.setCurrentText(classe)
    
    def clear_student_form(self):
        """Clear the student form fields"""
        self.student_code_massar.clear()
        self.student_name.clear()
        self.student_prenom.clear()
        self.student_cin.clear()
    
    def view_students(self):
        """Display all students in the table"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        try:
            self.cursor.execute("SELECT code_massar, cin, nom, prenom, classe FROM etudiants ORDER BY nom, prenom")
            students = self.cursor.fetchall()
            
            self.students_table.setRowCount(len(students))
            for row, student in enumerate(students):
                self.students_table.setItem(row, 0, QTableWidgetItem(student['code_massar']))
                self.students_table.setItem(row, 1, QTableWidgetItem(student['cin']))
                self.students_table.setItem(row, 2, QTableWidgetItem(student['nom']))
                self.students_table.setItem(row, 3, QTableWidgetItem(student['prenom']))
                self.students_table.setItem(row, 4, QTableWidgetItem(student['classe']))
            
            self.students_table.resizeColumnsToContents()
            self.update_status(f"{len(students)} étudiants chargés")
        except Error as e:
            self.update_status("Erreur de chargement étudiants")
            QMessageBox.critical(self, "Erreur", f"Échec de récupération: {str(e)}")
    
    def load_students(self):
        """Load students into the absence form dropdown"""
        if not self.db_connection:
            return
            
        try:
            self.cursor.execute("SELECT code_massar, nom, prenom FROM etudiants ORDER BY nom, prenom")
            students = self.cursor.fetchall()
            
            self.absence_student.clear()
            for student in students:
                display_text = f"{student['code_massar']} - {student['nom']} {student['prenom']}"
                self.absence_student.addItem(display_text, student['code_massar'])
        except Error as e:
            self.update_status("Erreur chargement liste étudiants")
            print(f"Erreur chargement étudiants: {str(e)}")
            
        
    
    def add_absence(self):
        """Add a new absence record"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        if self.absence_student.count() == 0:
            QMessageBox.warning(self, "Erreur", "Aucun étudiant disponible")
            return
            
        code_massar = self.absence_student.currentData()
        date = self.absence_date.date().toString("yyyy-MM-dd")
        reason = self.absence_reason.currentText()
        status = self.absence_status.currentText()
        notes = self.absence_notes.text().strip()
        
        try:
            self.cursor.execute(
                "INSERT INTO absences (code_massar, date_absence, raison, statut, notes) VALUES (%s, %s, %s, %s, %s)",
                (code_massar, date, reason, status, notes)
            )
            self.db_connection.commit()
            self.update_status("Absence enregistrée avec succès")
            QMessageBox.information(self, "Succès", "Absence enregistrée avec succès!")
            self.absence_date.setDate(QDate.currentDate())
            self.absence_notes.clear()
            self.view_absences()
        except Error as e:
            self.update_status("Erreur d'enregistrement absence")
            QMessageBox.critical(self, "Erreur", f"Échec d'enregistrement: {str(e)}")
    
    def update_absence(self):
        """Update an existing absence record"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        selected_row = self.absences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une absence à modifier")
            return
            
        absence_id = self.absences_table.item(selected_row, 0).text()
        code_massar = self.absence_student.currentData()
        date = self.absence_date.date().toString("yyyy-MM-dd")
        reason = self.absence_reason.currentText()
        status = self.absence_status.currentText()
        notes = self.absence_notes.text().strip()
        
        try:
            self.cursor.execute(
                """UPDATE absences SET code_massar=%s, date_absence=%s, raison=%s, statut=%s, notes=%s 
                WHERE id=%s""",
                (code_massar, date, reason, status, notes, absence_id)
            )
            self.db_connection.commit()
            self.update_status("Absence mise à jour avec succès")
            QMessageBox.information(self, "Succès", "Absence mise à jour avec succès!")
            self.view_absences()
        except Error as e:
            self.update_status("Erreur de mise à jour absence")
            QMessageBox.critical(self, "Erreur", f"Échec de mise à jour: {str(e)}")
    
    def delete_absence(self):
        """Delete an absence record"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        selected_row = self.absences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une absence à supprimer")
            return
            
        absence_id = self.absences_table.item(selected_row, 0).text()
        student_name = self.absences_table.item(selected_row, 2).text()
        date = self.absences_table.item(selected_row, 3).text()
        
        reply = QMessageBox.question(
            self, "Confirmation", 
            f"Voulez-vous vraiment supprimer l'absence de {student_name} du {date}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.cursor.execute("DELETE FROM absences WHERE id=%s", (absence_id,))
                self.db_connection.commit()
                self.update_status("Absence supprimée avec succès")
                QMessageBox.information(self, "Succès", "Absence supprimée avec succès!")
                self.view_absences()
            except Error as e:
                self.update_status("Erreur de suppression absence")
                QMessageBox.critical(self, "Erreur", f"Échec de suppression: {str(e)}")
    
    def absence_table_clicked(self, row, column):
        """Load absence data into form when clicked in table"""
        code_massar = self.absences_table.item(row, 1).text()
        date_str = self.absences_table.item(row, 3).text()
        reason = self.absences_table.item(row, 4).text()
        status = self.absences_table.item(row, 5).text()
        notes = self.absences_table.item(row, 6).text() if self.absences_table.item(row, 6) else ""
        
        # Find the student in the combo box
        index = self.absence_student.findData(code_massar)
        if index >= 0:
            self.absence_student.setCurrentIndex(index)
        
        date = QDate.fromString(date_str, "yyyy-MM-dd")
        self.absence_date.setDate(date)
        
        self.absence_reason.setCurrentText(reason)
        self.absence_status.setCurrentText(status)
        self.absence_notes.setText(notes)
    
    def view_absences(self):
        """Display filtered absences in the table"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        try:
            query = """
                SELECT a.id, e.code_massar, CONCAT(e.nom, ' ', e.prenom) AS nom_complet,
                       a.date_absence, a.raison, a.statut, a.notes, e.classe
                FROM absences a
                JOIN etudiants e ON a.code_massar = e.code_massar
                WHERE 1=1
            """
            
            params = []
            
            # Apply class filter
            selected_class = self.filter_class.currentText()
            if selected_class != "Toutes":
                query += " AND e.classe = %s"
                params.append(selected_class)
            
            # Apply status filter
            selected_status = self.filter_status.currentText()
            if selected_status != "Tous":
                query += " AND a.statut = %s"
                params.append(selected_status)
            
            # Apply date range filter
            date_from = self.filter_date_from.date().toString("yyyy-MM-dd")
            date_to = self.filter_date_to.date().toString("yyyy-MM-dd")
            query += " AND a.date_absence BETWEEN %s AND %s"
            params.extend([date_from, date_to])
            
            query += " ORDER BY a.date_absence DESC"
            
            self.cursor.execute(query, params)
            absences = self.cursor.fetchall()
            
            self.absences_table.setRowCount(len(absences))
            for row, absence in enumerate(absences):
                self.absences_table.setItem(row, 0, QTableWidgetItem(str(absence['id'])))
                self.absences_table.setItem(row, 1, QTableWidgetItem(absence['code_massar']))
                self.absences_table.setItem(row, 2, QTableWidgetItem(absence['nom_complet']))
                self.absences_table.setItem(row, 3, QTableWidgetItem(str(absence['date_absence'])))
                self.absences_table.setItem(row, 4, QTableWidgetItem(absence['raison']))
                
                status_item = QTableWidgetItem(absence['statut'])
                if absence['statut'] == "Justifie":
                    status_item.setBackground(QColor(144, 238, 144))  # Light green
                else:
                    status_item.setBackground(QColor(255, 182, 193))  # Light red
                self.absences_table.setItem(row, 5, status_item)
                
                notes_item = QTableWidgetItem(absence['notes'] if absence['notes'] else "")
                self.absences_table.setItem(row, 6, notes_item)
            
            self.update_status(f"{len(absences)} absences chargées")
        except Error as e:
            self.update_status("Erreur de chargement absences")
            QMessageBox.critical(self, "Erreur", f"Échec de récupération: {str(e)}")
    
    def generate_stats(self):
        """Generate absence statistiques"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        try:
            # Determine date range based on selected period
            period = self.stats_period.currentText()
            date_from = self.stats_date_from.date()
            date_to = self.stats_date_to.date()
            
            if period == "7 derniers jours":
                date_from = QDate.currentDate().addDays(-7)
            elif period == "30 derniers jours":
                date_from = QDate.currentDate().addDays(-30)
            elif period == "Ce mois":
                date_from = QDate(QDate.currentDate().year(), QDate.currentDate().month(), 1)
                date_to = QDate.currentDate()
            elif period == "Ce semestre":
                current_month = QDate.currentDate().month()
                if current_month <= 6:  # First semester
                    date_from = QDate(QDate.currentDate().year(), 1, 1)
                    date_to = QDate(QDate.currentDate().year(), 6, 30)
                else:  # Second semester
                    date_from = QDate(QDate.currentDate().year(), 7, 1)
                    date_to = QDate(QDate.currentDate().year(), 12, 31)
            
            # Update date fields
            self.stats_date_from.setDate(date_from)
            self.stats_date_to.setDate(date_to)
            
            date_from_str = date_from.toString("yyyy-MM-dd")
            date_to_str = date_to.toString("yyyy-MM-dd")
            
            query = """
                SELECT 
                    e.classe,
                    COUNT(*) AS total_absences,
                    SUM(CASE WHEN a.statut = 'Justifié' THEN 1 ELSE 0 END) AS justified,
                    SUM(CASE WHEN a.statut = 'Non justifié' THEN 1 ELSE 0 END) AS unjustified,
                    COUNT(DISTINCT a.code_massar) AS students_affected,
                    (SELECT COUNT(*) FROM etudiants WHERE classe = e.classe) AS total_students
                FROM absences a
                JOIN etudiants e ON a.code_massar = e.code_massar
                WHERE a.date_absence BETWEEN %s AND %s
            """
            
            params = [date_from_str, date_to_str]
            
            # Apply class filter
            selected_class = self.stats_class.currentText()
            if selected_class != "Toutes":
                query += " AND e.classe = %s"
                params.append(selected_class)
            
            query += " GROUP BY e.classe ORDER BY e.classe"
            
            self.cursor.execute(query, params)
            stats = self.cursor.fetchall()
            
            # Generate report
            report = f"Rapport des absences du {date_from_str} au {date_to_str}\n\n"
            report += "="*50 + "\n\n"
            
            if not stats:
                report += "Aucune absence enregistrée pour cette période.\n"
            else:
                for stat in stats:
                    report += f"Classe: {stat['classe']}\n"
                    report += f"- Total des absences: {stat['total_absences']}\n"
                    report += f"  - Justifiées: {stat['justified']} ({stat['justified']/stat['total_absences']:.1%})\n"
                    report += f"  - Non justifiées: {stat['unjustified']} ({stat['unjustified']/stat['total_absences']:.1%})\n"
                    report += f"- Étudiants concernés: {stat['students_affected']}/{stat['total_students']}\n"
                    report += f"- Taux d'absence moyen: {stat['total_absences']/stat['total_students']:.1f} absences/étudiant\n\n"
            
            # Add top absent students
            query = """
                SELECT 
                    e.nom, e.prenom, e.classe,
                    COUNT(*) AS absence_count
                FROM absences a
                JOIN etudiants e ON a.code_massar = e.code_massar
                WHERE a.date_absence BETWEEN %s AND %s
                GROUP BY a.code_massar
                ORDER BY absence_count DESC
                LIMIT 5
            """
            
            self.cursor.execute(query, [date_from_str, date_to_str])
            top_absent = self.cursor.fetchall()
            
            if top_absent:
                report += "Top 5 des étudiants les plus absents:\n"
                for i, student in enumerate(top_absent, 1):
                    report += f"{i}. {student['nom']} {student['prenom']} ({student['classe']}): {student['absence_count']} absences\n"
            
            self.stats_display.setPlainText(report)
            self.update_status("Statistiques générées avec succès")
            
        except Error as e:
            self.update_status("Erreur de génération statistiques")
            QMessageBox.critical(self, "Erreur", f"Échec de génération: {str(e)}")
    
    def export_students_csv(self):
        """Export students data to CSV"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les étudiants", "", "CSV Files (*.csv)")
            
            if not filename:  # User cancelled
                return
                
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['Code Massar', 'CIN', 'Nom', 'Prénom', 'Classe', 'Date Ajout'])
                
                # Fetch data in chunks
                self.cursor.execute("SELECT * FROM etudiants ORDER BY nom, prenom")
                while True:
                    batch = self.cursor.fetchmany(100)
                    if not batch:
                        break
                    for row in batch:
                        writer.writerow([
                            row['code_massar'],
                            row['cin'],
                            row['nom'],
                            row['prenom'],
                            row['classe'],
                        ])
            
            self.update_status(f"Étudiants exportés vers {filename}")
            QMessageBox.information(self, "Succès", f"Données exportées vers {filename}")
        except Exception as e:
            self.update_status("Erreur d'export étudiants")
            QMessageBox.critical(self, "Erreur", f"Échec d'export: {str(e)}")
    
    def export_absences_csv(self):
        """Export absences data to CSV"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Exporter les absences", "", "CSV Files (*.csv)")
            
            if not filename:  # User cancelled
                return
                
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(['ID', 'Code Massar', 'Nom', 'Prenom', 'Classe', 'Date', 'Raison', 'Statut', 'Notes'])
                
                # Build the same query as view_absences for consistency
                query = """
                    SELECT a.id, e.code_massar, e.nom, e.prenom, e.classe,
                           a.date_absence, a.raison, a.statut, a.notes
                    FROM absences a
                    JOIN etudiants e ON a.code_massar = e.code_massar
                    WHERE 1=1
                """
                
                params = []
                
                # Apply class filter
                selected_class = self.filter_class.currentText()
                if selected_class != "Toutes":
                    query += " AND e.classe = %s"
                    params.append(selected_class)
                
                # Apply status filter
                selected_status = self.filter_status.currentText()
                if selected_status != "Tous":
                    query += " AND a.statut = %s"
                    params.append(selected_status)
                
                # Apply date range filter
                date_from = self.filter_date_from.date().toString("yyyy-MM-dd")
                date_to = self.filter_date_to.date().toString("yyyy-MM-dd")
                query += " AND a.date_absence BETWEEN %s AND %s"
                params.extend([date_from, date_to])
                
                query += " ORDER BY a.date_absence DESC"
                
                self.cursor.execute(query, params)
                
                while True:
                    batch = self.cursor.fetchmany(100)
                    if not batch:
                        break
                    for row in batch:
                        writer.writerow([
                            row['id'],
                            row['code_massar'],
                            row['nom'],
                            row['prenom'],
                            row['classe'],
                            str(row['date_absence']),
                            row['raison'],
                            row['statut'],
                            row['notes'] if row['notes'] else ""
                        ])
            
            self.update_status(f"Absences exportées vers {filename}")
            QMessageBox.information(self, "Succès", f"Données exportées vers {filename}")
        except Exception as e:
            self.update_status("Erreur d'export absences")
            QMessageBox.critical(self, "Erreur", f"Échec d'export: {str(e)}")
    
    def export_data(self):
        """Export both students and absences to CSV files"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        try:
            # Get directory to save files
            directory = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de destination")
            if not directory:
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export etudiant
            students_file = os.path.join(directory, f"etudiants_{timestamp}.csv")
            with open(students_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['Code Massar', 'CIN', 'Nom', 'Prénom', 'Classe', 'Date Ajout'])
                
                self.cursor.execute("SELECT * FROM etudiants ORDER BY nom, prenom")
                for row in self.cursor:
                    writer.writerow([
                        row['code_massar'],
                        row['cin'],
                        row['nom'],
                        row['prenom'],
                        row['classe'],
                        str(row['date_ajout'])
                    ])
            
            # Export absences
            absences_file = os.path.join(directory, f"absences_{timestamp}.csv")
            with open(absences_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['ID', 'Code Massar', 'Nom', 'Prénom', 'Classe', 'Date', 'Raison', 'Statut', 'Notes'])
                
                self.cursor.execute("""
                    SELECT a.id, e.code_massar, e.nom, e.prenom, e.classe,
                           a.date_absence, a.raison, a.statut, a.notes
                    FROM absences a
                    JOIN etudiants e ON a.code_massar = e.code_massar
                    ORDER BY a.date_absence DESC
                """)
                
                for row in self.cursor:
                    writer.writerow([
                        row['id'],
                        row['code_massar'],
                        row['nom'],
                        row['prenom'],
                        row['classe'],
                        str(row['date_absence']),
                        row['raison'],
                        row['statut'],
                        row['notes'] if row['notes'] else ""
                    ])
            
            self.update_status(f"Données exportées vers {directory}")
            QMessageBox.information(
                self, "Succès", 
                f"Données exportées avec succès:\n{students_file}\n{absences_file}"
            )
        except Exception as e:
            self.update_status("Erreur d'export données")
            QMessageBox.critical(self, "Erreur", f"Échec d'export: {str(e)}")
            
    def auto_save_backup(self):
        """Automatically save backup at regular intervals"""
        if not self.db_connection:
            return
            
        try:
            # Create backup directory if it doesn't exist
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"auto_backup_{timestamp}.sql")
            
            # Get all tables data
            tables = ['etudiants', 'absences']
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                for table in tables:
                    # ecrire les table 
                    self.cursor.execute(f"SHOW CREATE TABLE {table}")
                    create_table = self.cursor.fetchone()['Create Table']
                    f.write(f"{create_table};\n\n")
                    
                    # Write table data
                    self.cursor.execute(f"SELECT * FROM {table}")
                    rows = self.cursor.fetchall()
                    
                    if rows:
                        columns = list(rows[0].keys())
                        f.write(f"INSERT INTO {table} ({', '.join(columns)}) VALUES\n")
                        
                        for i, row in enumerate(rows):
                            values = []
                            for col in columns:
                                val = row[col]
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    values.append(f"'{str(val).replace("'", "''")}'")
                            
                            f.write(f"({', '.join(values)})")
                            if i < len(rows) - 1:
                                f.write(",\n")
                            else:
                                f.write(";\n\n")
            
            #
            backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("auto_backup_")])
            while len(backups) > 5:
                os.remove(os.path.join(backup_dir, backups[0]))
                backups = backups[1:]
            
            self.update_status(f"Sauvegarde automatique créée: {backup_file}")
        except Exception as e:
            self.update_status("Erreur de sauvegarde automatique")
            print(f"Erreur de sauvegarde automatique: {str(e)}")
    
    def open_email_dialog(self):
        """Open the email sending dialog"""
        if not self.db_connection:
            QMessageBox.warning(self, "Erreur", "Veuillez vous connecter d'abord")
            return
            
        dialog = EmailSender(self)
        dialog.exec_()
    
    def open_settings(self):
        """Open application settings dialog"""
        QMessageBox.information(self, "Paramètres", "Cette fonctionnalité est en développement.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Gestion des Absences BTS</h2>
        <p>Version 1.0</p>
        <p>Une application pour gérer les absences des étudiants BTS.</p>
        <p>Développé par Hamza dine et soufian amzil</p>
        <p>&copy; 2025 Tous droits réservés</p>
        """
        QMessageBox.about(self, "À propos", about_text)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(message)
        print(message)  
    
    def load_last_session(self):
        """Load last session settings"""
        config = configparser.ConfigParser()
        if os.path.exists('app_config.ini'):
            config.read('app_config.ini')
            if 'DATABASE' in config:
                self.host_input.setText(config['DATABASE'].get('host', 'localhost'))
                self.user_input.setText(config['DATABASE'].get('user', 'root'))
                self.db_input.setText(config['DATABASE'].get('database', 'gestion_absences_BTS'))
    
    def save_session(self):
        """Save current session settings"""
        config = configparser.ConfigParser()
        config['DATABASE'] = {
            'host': self.host_input.text(),
            'user': self.user_input.text(),
            'database': self.db_input.text()
        }
        with open('app_config.ini', 'w') as configfile:
            config.write(configfile)
    
    def apply_styles(self):
        """Apply CSS styling to the application"""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 25px;
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #4CAF50;
            }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: white;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 6px;
                border: none;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                margin-top: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #f1f1f1;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #4CAF50;
            }
            QTabBar::tab:hover {
                background: #e9e9e9;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QStatusBar {
                background-color: #e0e0e0;
                border-top: 1px solid #ccc;
            }
            QMenuBar {
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #e0e0e0;
            }
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
                color: white;
            }
           
        """)
        
        # Additional styling for specific widgets
        self.status_bar.setStyleSheet("""
            QStatusBar {
                font-size: 11px;
                color: #555;
            }
        """)
        
        self.stats_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.save_session()
        self.disconnect_db()
        
        # Confirm exit
        reply = QMessageBox.question(
            self, 'Confirmation',
            'Êtes-vous sûr de vouloir quitter?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = AbsenceApp()
    window.show()
    sys.exit(app.exec_())