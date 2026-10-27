from datetime import datetime
import pandas as pd
import psycopg2

# Configuration de la base de données PostgreSQL
DB_CONFIG = {
    'dbname': 'cartographie_meal',
    'user': 'postgres',
    'password': 'corporate2019',
    'host': 'localhost',
    'port': '5432',
}

TABLE_USER = "auth_user"
TABLE_PERSONNEL = "cartographie_personnel"


def convertir_entier(val):
    """Convertit proprement une valeur en entier ou retourne None."""
    if pd.isna(val) or val is None or str(val).strip() == '':
        return None
    try:
        val_str = str(val).strip()
        if val_str.endswith('.0'):
            val_str = val_str[:-2]
        return int(float(val_str))
    except (ValueError, TypeError):
        return None


def convertir_date(date_val):
    """Convertit proprement une date en format YYYY-MM-DD."""
    if pd.isna(date_val) or not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val.strftime('%Y-%m-%d')
    date_str = str(date_val).strip()
    for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None


def nettoyer_valeur(valeur):
    if pd.isna(valeur) or valeur is None:
        return None
    val_str = str(valeur).strip()
    if val_str in ['', 'nan', 'NaN', 'None', 'null', 'NULL', '#REF!']:
        return None
    if val_str.endswith('.0'):
        val_str = val_str[:-2]
    return val_str if val_str else None


def normaliser_booleen(valeur):
    """Convertit une valeur Excel en booléen True/False."""
    if pd.isna(valeur) or valeur is None:
        return False
    if isinstance(valeur, bool):
        return valeur
    val_str = str(valeur).strip().upper()
    if val_str in ['1', 'TRUE', 'VRAI', 'YES', 'OUI', 'T']:
        return True
    return False


def vider_et_inserer_donnees(fichier_excel='personnel-meal.xlsx'):
    conn = None
    try:
        print("🔌 Connexion à PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # ==========================================
        # ÉTAPE 0 : Vider complètement les tables existantes
        # ==========================================
        print("🗑️ Vidage complet des tables (CASCADE)...")
        # On vide personnel d'abord, puis user, avec remise à zéro des IDs (RESTART IDENTITY)
        cursor.execute(f"TRUNCATE TABLE {TABLE_PERSONNEL}, {TABLE_USER} RESTART IDENTITY CASCADE;")
        conn.commit()
        print("  -> Tables vidées avec succès.")

        print(f"📖 Lecture du fichier Excel : {fichier_excel}...")
        df = pd.read_excel(fichier_excel)

        sql_insert_user = f"""
            INSERT INTO {TABLE_USER} (
                username, password, first_name, last_name, email, 
                is_staff, is_active, is_superuser, date_joined
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id;
        """

        sql_insert_personnel = f"""
            INSERT INTO {TABLE_PERSONNEL} (
                nom, prenom, mail, tel, photo, sexe, bd_user_id, fonction, 
                country, pays, ville, is_active, nationalite, code, 
                parcours_meal, date_enregistrement, years_expertise, 
                level_expertise, is_speeck_french, is_speeck_english, 
                other_language, bio, profil_linkedin, organization_type, 
                fonction_organization, cartographie_is_valid, longitude, 
                lattitude, consentement
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, %s, 
                %s, %s, %s, 
                %s, %s
            );
        """

        nb_utilisateurs_ajoutes = 0
        nb_personnels_ajoutes = 0

        print("⚙️ Début de l'insertion séquentielle (Auth_User d'abord, puis Personnel)...")

        for _, row in df.iterrows():
            username = nettoyer_valeur(row.get('Username'))
            if not username:
                continue
            
            password = nettoyer_valeur(row.get('Password')) or 'pbkdf2_sha256$600000$dummy$...'
            first_name = nettoyer_valeur(row.get('First Name')) or username
            last_name = nettoyer_valeur(row.get('Last Name')) or '-'
            email = nettoyer_valeur(row.get('Email')) or f"{username}@example.com"
            
            is_staff = normaliser_booleen(row.get('Is Staff'))
            is_active_user = normaliser_booleen(row.get('Is Active'))
            is_superuser = normaliser_booleen(row.get('Is Superuser'))

            # Données associées Personnel
            nom = nettoyer_valeur(row.get('Ctn Bpf Personnel → Nom')) or last_name
            prenom = nettoyer_valeur(row.get('Ctn Bpf Personnel → Prenom')) or first_name
            mail = nettoyer_valeur(row.get('Ctn Bpf Personnel → Mail')) or email
            tel = nettoyer_valeur(row.get('Ctn Bpf Personnel → Tel'))
            photo = nettoyer_valeur(row.get('Ctn Bpf Personnel → Photo'))
            sexe = nettoyer_valeur(row.get('Ctn Bpf Personnel → Sexe'))
            fonction = nettoyer_valeur(row.get('Ctn Bpf Personnel → Fonction'))
            country = nettoyer_valeur(row.get('Ctn Bpf Personnel → Country'))
            pays = nettoyer_valeur(row.get('Ctn Bpf Personnel → Pays')) or 'Non renseigné'
            ville = nettoyer_valeur(row.get('Ctn Bpf Personnel → Ville')) or 'Non renseignée'
            is_active_pers = normaliser_booleen(row.get('Ctn Bpf Personnel → Is Active'))
            nationalite = nettoyer_valeur(row.get('Ctn Bpf Personnel → Nationalite'))
            code = nettoyer_valeur(row.get('Ctn Bpf Personnel → Code'))
            parcours_meal = nettoyer_valeur(row.get('Ctn Bpf Personnel → Parcours Meal'))
            date_enregistrement = convertir_date(row.get('Ctn Bpf Personnel → Date Enregistrement'))
            years_expertise = convertir_entier(row.get('Ctn Bpf Personnel → Years Expertise'))
            level_expertise = nettoyer_valeur(row.get('Ctn Bpf Personnel → Level Expertise'))
            is_speeck_french = normaliser_booleen(row.get('Ctn Bpf Personnel → Is Speeck French'))
            is_speeck_english = normaliser_booleen(row.get('Ctn Bpf Personnel → Is Speeck English'))
            other_language = nettoyer_valeur(row.get('Ctn Bpf Personnel → Other Language')) or ''
            bio = nettoyer_valeur(row.get('Ctn Bpf Personnel → Bio'))
            profil_linkedin = nettoyer_valeur(row.get('Ctn Bpf Personnel → Profil Linkedin'))
            organization_type = nettoyer_valeur(row.get('Ctn Bpf Personnel → Organization Type'))
            fonction_organization = nettoyer_valeur(row.get('Ctn Bpf Personnel → Fonction Organization'))
            cartographie_is_valid = normaliser_booleen(row.get('Ctn Bpf Personnel → Cartographie Is Valid'))
            longitude = convertir_entier(row.get('Ctn Bpf Personnel → Longitude'))
            lattitude = convertir_entier(row.get('Ctn Bpf Personnel → Lattitude'))
            consentement = normaliser_booleen(row.get('Ctn Bpf Personnel → Consentement'))

            try:
                # 1. Insertion de l'utilisateur dans auth_user et récupération de son ID généré
                cursor.execute(
                    sql_insert_user,
                    (username, password, first_name, last_name, email, is_staff, is_active_user, is_superuser)
                )
                user_id = cursor.fetchone()[0]
                nb_utilisateurs_ajoutes += 1

                # 2. Insertion du profil Personnel lié avec l'ID utilisateur obtenu
                cursor.execute(
                    sql_insert_personnel,
                    (
                        nom, prenom, mail, tel, photo, sexe, user_id, fonction,
                        country, pays, ville, is_active_pers, nationalite, code,
                        parcours_meal, date_enregistrement, years_expertise,
                        level_expertise, is_speeck_french, is_speeck_english,
                        other_language, bio, profil_linkedin, organization_type,
                        fonction_organization, cartographie_is_valid, longitude,
                        lattitude, consentement
                    )
                )
                nb_personnels_ajoutes += 1
                conn.commit()  # Valide les deux insertions pour cette ligne
                print(f"  ➕ Succès : User '{username}' lié au Personnel [{code}] {nom} {prenom}")

            except Exception as e:
                conn.rollback()  # Annule uniquement cette ligne en cas d'erreur pour ne pas bloquer les autres
                print(f"  ❌ Erreur pour l'utilisateur {username}: {e}")

        print(f"\n✅ Importation globale terminée avec succès !")
        print(f"  - Total comptes utilisateurs insérés : {nb_utilisateurs_ajoutes}")
        print(f"  - Total profils personnel insérés : {nb_personnels_ajoutes}")

    except Exception as error:
        print(f"❌ Erreur critique générale : {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("🔒 Connexion fermée.")


if __name__ == '__main__':
    vider_et_inserer_donnees()
