from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import logging
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





logger = logging.getLogger(__name__)
@shared_task
def send_otp_email_task(email, nom_personnel, code_genere):
    try:
        sujet = "Votre code de vérification OTP"
        context = {
            'nom_personnel': nom_personnel,
            'code_genere': code_genere,
        }
        
        # Rendu du template HTML
        html_content = render_to_string('webpages/emails/code-verification.html', context)
        text_content = strip_tags(html_content) 
        
        # Envoi de l'e-mail (Via SMTP configuré dans les settings)
        email_message = EmailMultiAlternatives(
            subject=sujet,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)
        
        logger.info(f"E-mail OTP envoyé avec succès à {email} via Celery/Redis.")
    except Exception as e:
        logger.error(f"Erreur d'envoi de l'e-mail en arrière-plan pour {email} : {str(e)}")