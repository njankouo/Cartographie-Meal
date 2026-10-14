from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_expert_registration_email(expert_data):
    print("--- DÉBUT DE LA TÂCHE CELERY ---")
    print(f"Données reçues : {expert_data}")

    try:
        fullname = expert_data.get('fullname', 'Inconnu')
        country = expert_data.get('country', 'Non spécifié')
        recipient_email = expert_data.get('email')  # <-- Récupère l'email du formulaire

        if not recipient_email:
            print("--- AUCUN EMAIL FOURNI ---")
            return

        subject = f"Bienvenue {fullname} !"
        message = (
            f"Bonjour {fullname},\n\n"
            f"Merci pour votre inscription en tant qu'expert MEAL.\n"
            f"Pays : {country}\n\n"
            f"Cordialement,\nL'équipe MEAL"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Ton email d'expéditeur
            [recipient_email],  # Envoie à l'utilisateur qui a rempli le formulaire
            fail_silently=False,
        )
        print(f"--- MAIL ENVOYÉ AVEC SUCCÈS À {recipient_email} ---")

    except Exception as e:
        print(f"--- ERREUR DANS LA TÂCHE : {str(e)} ---")