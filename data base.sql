
CREATE DATABASE IF NOT EXISTS gestion_absences_bts;
USE gestion_absences_bts;

CREATE TABLE IF NOT EXISTS etudiants (
    code_massar VARCHAR(50) PRIMARY KEY,
    cin VARCHAR(50) UNIQUE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    classe VARCHAR(20) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
                );
drop database gestion_absences_BTS;
