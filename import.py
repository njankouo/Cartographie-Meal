import os
import sys
import pandas as pd

# Chemin absolu de la racine de votre projet Django
PROJECT_DIR = '/home/blackprotocol/Documents/Cartographie-Meal'
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

from django.conf import settings

# 1. Configuration manuelle de Django et de la base de données
if not settings.configured:
    settings.configure(
        DEBUG=False,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'cartographie_meal',
                'USER': 'postgres',
                'PASSWORD': 'corporate2019',
                'HOST': 'localhost',
                'PORT': '5432'
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'cartographie',  # Votre application Django
        ],
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

import django
django.setup()

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.db import transaction
from cartographie.models import Personnel

def verifier_et_importer():
    fichier = '/home/blackprotocol/Downloads/personnel-meal-final.xlsx'
    
    print("--- ÉTAPE 1 : Vérification du fichier Excel ---")
    if not os.path.exists(fichier):
        print(f"❌ Erreur : Le fichier est introuvable à l'emplacement : {fichier}")
        return
    print(f"✅ Fichier trouvé : {fichier}")

    print("\n--- ÉTAPE 2 : Lecture des données avec Pandas ---")
    try:
        df = pd.read_excel(fichier)
        print(f"✅ Fichier lu avec succès. Nombre total de lignes : {len(df)}")
        # Affichage des en-têtes détectés pour vérifier s'ils correspondent à vos colonnes
        print(f"📋 En-têtes (colonnes) détectés dans le fichier :\n{list(df.columns)}")
    except Exception as e:
        print(f"❌ Erreur critique lors de la lecture du fichier Excel : {e}")
        return

    nb_importes = 0
    nb_erreurs = 0

    print("\n--- ÉTAPE 3 : Traitement et insertion ligne par ligne ---")
    for index, row in df.iterrows():
        # Nettoyage des valeurs et gestion des majuscules/minuscules dans les clés
        data = {str(k).strip(): (str(v).strip() if pd.notna(v) else "") for k, v in row.items()}
        
        # Recherche élargie des champs pour éviter les erreurs de casse (ex: 'Email' vs 'email')
        email = (
            data.get('mail') or data.get('email') or 
            data.get('Mail') or data.get('Email') or 
            data.get('MAIL') or data.get('EMAIL')
        )
        username = (
            data.get('username') or data.get('Username') or 
            data.get('USERNAME') or email
        )

        # Vérification 1 : Présence des champs obligatoires
        if not email or not username:
            print(f"⚠️ Ligne {index + 2} ignorée : Email ou Username manquant (Valeurs lues -> email: '{email}', username: '{username}')")
            nb_erreurs += 1
            continue

        # Vérification 2 : Validation stricte du format de l'e-mail
        try:
            validate_email(email)
        except ValidationError:
            print(f"⚠️ Ligne {index + 2} ignorée : Format d'e-mail invalide ou mal formé ('{email}')")
            nb_erreurs += 1
            continue

        try:
            with transaction.atomic():
                # Récupération sécurisée des autres champs avec gestion de la casse
                prenom = data.get('prenom') or data.get('Prénom') or data.get('PRENOM') or ''
                nom = data.get('nom') or data.get('Nom') or data.get('NOM') or ''
                tel = data.get('tel') or data.get('telephone') or data.get('Tel') or data.get('Téléphone') or ''
                country = data.get('country') or data.get('Country') or data.get('pays') or data.get('Pays') or 'Inconnu'
                ville = data.get('ville') or data.get('Ville') or 'Inconnue'
                sexe = data.get('sexe') or data.get('Sexe') or ''
                fonction = data.get('fonction') or data.get('Fonction') or ''
                code = data.get('code') or data.get('Code') or ''
                nationalite = data.get('nationalite') or data.get('Nationalité') or ''

                # Création ou mise à jour du User Django
                user, user_created = User.objects.update_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': prenom,
                        'last_name': nom,
                    }
                )

                # Création ou mise à jour de l'enregistrement Personnel
                personnel, pers_created = Personnel.objects.update_or_create(
                    mail=email,
                    defaults={
                        'nom': nom,
                        'prenom': prenom,
                        'tel': tel,
                        'country': country,
                        'ville': ville,
                        'sexe': sexe,
                        'fonction': fonction,
                        'code': code,
                        'nationalite': nationalite,
                        'bd_user': user,
                        'cartographie_is_valid': False,
                    }
                )
                
                nb_importes += 1
                statut = "Créé" if pers_created else "Mis à jour"
                print(f"✅ Ligne {index + 2} : Succès ({statut}) pour {email}")

        except Exception as e:
            nb_erreurs += 1
            print(f"❌ Erreur base de données à la ligne {index + 2} pour l'email '{email}' : {repr(e)}")

    print(f"\n--- BILAN FINAL DE L'IMPORTATION ---")
    print(f"✅ Total enregistrements importés / mis à jour avec succès : {nb_importes}")
    print(f"❌ Total erreurs rencontrées : {nb_erreurs}")

if __name__ == '__main__':
    verifier_et_importer()
