from django.shortcuts import render
from django_countries import countries
from .models import *
from django.db.models import Count, Q
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_expert_registration_email, send_otp_email_task
import logging
import random
import string
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from cities_light.models import City
from django.core.exceptions import ObjectDoesNotExist
import pycountry
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'webpages/index.html')

def MealAfrique(request):
    # 1. Vérification sécurisée de la session (évite le KeyError si la clé n'existe pas)
    if request.session.get('personnel_code'):
        return redirect('Information-members')

    # 2. Total du personnel
    personnel = Personnel.objects.count()

    # Récupération du nombre total de membres par pays
    country_counts = Personnel.objects.values('country') \
                                       .annotate(total=Count('id')) \
                                       .order_by('country')

    # Création d'un dictionnaire des pays avec leur code et le nombre de membres
    country_data = {
        country['country']: {
            'total': country['total'],
            'name': country['country'],  
        }
        for country in country_counts
    }

    # Nombre total de pays distincts
    total_countries = Personnel.objects.values('country').distinct().count()

    # Passage des données au template
    context = {
        'personnel': personnel,
        'country_data': country_data,
        'members': Personnel.objects.all(),
        'total_countries': total_countries, 
        'countries': countries, # Pensez à définir 'countries' si ce n'est pas déjà fait ailleurs
    }

    return render(request, 'webpages/inscription.html', context)

def CountMembers(request):
    personnel = Personnel.objects.count()
    return JsonResponse({'personnel':personnel})
from django.core.mail import EmailMultiAlternatives # <-- Import important
from django.template.loader import render_to_string # <-- Import important
from django.utils.html import strip_tags
@csrf_exempt  
def check_email_ajax(request):
    if request.method != "POST":
        return JsonResponse({"exists": False, "error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"exists": False, "error": "Données invalides"}, status=400)

    if not email:
        return JsonResponse({"exists": False, "error": "Email vide"}, status=400)

    # Recherche du personnel
    personne = Personnel.objects.filter(mail=email).first()
    if not personne:
        return JsonResponse({"exists": False, "error": "Aucun personnel trouvé avec cet email"}, status=404)

    try:
        # Génération d'un code à 6 chiffres
        code_genere = f"{random.randint(0, 999999):06d}"
        
        # Expiration fixée à 5 minutes
        expiration_time = timezone.now() + datetime.timedelta(minutes=5)
        
        # Invalidation des anciens codes non utilisés pour ce personnel
        OtpPersonnel.objects.filter(personnel=personne, is_used=False).update(is_used=True)
        
        # Création du nouvel OTP en base
        OtpPersonnel.objects.create(
            personnel=personne,
            code=code_genere,
            expires_at=expiration_time
        )
        
        nom_personnel = getattr(personne, 'nom', 'Utilisateur')

        # --- ENVOI ASYNCHRONE VIA REDIS / CELERY ---
        # .delay() envoie la tâche dans la file d'attente Redis instantanément
        send_otp_email_task.delay(email, nom_personnel, code_genere)
        # -------------------------------------------
        
        # SÉCURITÉ : Stockage de l'email en session
        request.session['otp_email'] = email
        
        return JsonResponse({
            "exists": True, 
            "message": "Requête traitée. Le code sera envoyé sous peu."
        })
        
    except Exception as e:
        return JsonResponse({"exists": False, "error": f"Erreur serveur : {str(e)}"}, status=500)
logger = logging.getLogger(__name__)

def register_expert(request):
    if request.method == "POST":
        try:
            # 1. Récupération des données
            fullname = request.POST.get('fullname')
            whatsapp = request.POST.get('whatsapp') # Vérifie bien l'orthographe dans le HTML
            email = request.POST.get('email')
            country = request.POST.get('country')
            gender = request.POST.get('gender')
            photo = request.FILES.get('photo')
            nationalite = request.POST.get('nationalite')

            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            code = f"MEAL-AF-{country}-{random_part}"
            
            if not email:
                return JsonResponse({"status": "error", "message": "L'email est requis"}, status=400)

            # 2. Gestion de l'utilisateur (Éviter le crash si l'email existe déjà)
            if User.objects.filter(username=email).exists():
                expert = User.objects.get(username=email)
            else:
                # On utilise create_user pour gérer correctement le password et le hashage
                expert = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=fullname
                )

            
            personnel, created = Personnel.objects.update_or_create(
                bd_user=expert,
                defaults={

                    'tel': whatsapp,
                    'country': country,
                    'sexe': gender,
                    'mail': email,
                    'photo':photo,
                    'nom': fullname,
                    'nationalite': nationalite,
                    'code': code,
                    'parcours_meal': request.POST.get('parcours_meal'),
                    'fonction': request.POST.get('skill'),
                    'date_enregistrement': timezone.now()
                    
                }
            )

            # 4. Préparation des données pour Celery
            expert_info = {
                'fullname': fullname,
                'country': country,
                'whatsapp': whatsapp,
                'email': email
            }

            # 5. Envoi au Broker
            send_expert_registration_email.delay(expert_info)

            request.session['identification_user'] = expert.id

            return JsonResponse({"status": "success"})

        except Exception as e:
           
            return JsonResponse({"status": "error", "message": f"Erreur Django: {str(e)}"}, status=400)

    return JsonResponse({"status": "error", "message": "Méthode non autorisée"}, status=405)
def Information_members(request):
    template = 'webpages/infos-member.html'

    # 1. Vérification de sécurité : l'utilisateur est-il passé par l'OTP ?
    personnel_code = request.session.get('personnel_code')
    if not personnel_code:
        return redirect('check_email_page')

    # 2. Récupération du personnel
    personnel = get_object_or_404(Personnel, code=personnel_code)

    context = {
        'personnel': personnel
    }

    return render(request, template, context)

def check_email_page(request):
    if request.session.get('personnel_code'):
        return redirect('Information-members')
    return render(request, 'webpages/check_email_page.html')
from cities_light.models import City, Country
def Cartographie(request):
    # 1. Vérification sécurisée de la session
    personne_code = request.session.get('personnel_code')
    if not personne_code:
        return redirect('check_email_page')
    
    # 2. Récupération du personnel
    try:
        personnel = Personnel.objects.get(code=personne_code)
    except Personnel.DoesNotExist:
        request.session.flush()
        return redirect('check_email_page')
    
    # 3. Extraction des ID déjà associés à l'utilisateur sous forme de listes
    user_profil_ids = list(
        ProfilPersonnel.objects.filter(personnel=personnel).values_list('profil_id', flat=True)
    )
    user_domaine_ids = list(
        PersonnelDomaine.objects.filter(personnel=personnel).values_list('domaine_id', flat=True)
    )
    user_secteur_ids = list(
        PersonnelSecteurIntervention.objects.filter(personnel=personnel).values_list('secteur_intervention_id', flat=True)
    )
    user_outil_ids = list(
        PersonnelOutilMeal.objects.filter(personnel=personnel).values_list('outil_meal_id', flat=True)
    )
    user_disponibilite_ids = list(
        PersonnelDisponibilityType.objects.filter(personnel=personnel).values_list('type_disponibilite_id', flat=True)
    )

    # Extraction des années d'expérience par profil (Format dictionnaire { "profil_id": annees })
    user_profil_experiences = {
        str(p.profil_id): p.year_experience 
        for p in ProfilPersonnel.objects.filter(personnel=personnel) 
        if p.year_experience is not None
    }

    # 4. Préparation du contexte
    context = {
        'countries': Country.objects.all().order_by('name'),
        'personnel': personnel,
        'domaine_expertise': DomaineExpertise.objects.all(),
        'profils': ProfilMeal.objects.all(),
        'secteurs': SecteurIntervention.objects.all(),
        'outils': OutilsMeal.objects.all(),
        'types_disponibilite': DisponibilityType.objects.all(),

        # Listes d'IDs pré-sélectionnés pour le template
        'user_profil_ids': user_profil_ids,
        'user_domaine_ids': user_domaine_ids,
        'user_secteur_ids': user_secteur_ids,
        'user_outil_ids': user_outil_ids,
        'user_disponibilite_ids': user_disponibilite_ids,
        
        # Années d'expérience sérialisées en JSON pour le JS
        'user_profil_experiences_json': json.dumps(user_profil_experiences),
    }

    return render(request, 'webpages/cartographie.html', context)
def get_cities_by_country(request):
    """
    API endpoint pour récupérer les villes selon le NOM du pays (ou son ID/Code)
    """
    country_val = request.GET.get('country')
    
    if not country_val:
        return JsonResponse({'cities': []})

    try:
        # 1. Si c'est un ID numérique
        if country_val.isdigit():
            cities = City.objects.filter(country_id=country_val)
        else:
            # 2. Recherche par NOM du pays (exact ou insensible à la casse avec __iexact)
            cities = City.objects.filter(country__name__iexact=country_val)
            
            # Si aucune ville n'est trouvée par le nom complet, tente de chercher par code ISO (code2 / code3)
            if not cities.exists():
                cities = City.objects.filter(
                    country__code2__iexact=country_val
                ) | City.objects.filter(
                    country__code3__iexact=country_val
                )

        # Extraction des champs 'id' et 'name' triés par ordre alphabétique
        cities_list = list(cities.order_by('name').values('id', 'name'))

    except Exception as e:
        cities_list = []

    return JsonResponse({'cities': cities_list})

def EditProfil(request):
    template = 'webpages/edit-profil.html'
    personnel_code = request.session.get('personnel_code')
    personnel = Personnel.objects.get(code=personnel_code)

    context ={
    'personnel':personnel,
    'countries': countries,
    }

    return render(request, template, context)

def Updateprofil(request):
    if request.method == 'POST':
        try:
           
            nom = request.POST.get('fullname')
            nationalite = request.POST.get('nationalite')
            country = request.POST.get('country')
            personnel_id = request.POST.get('personnel')
            parcours_meal = request.POST.get('parcours_meal')
            fonction = request.POST.get('skill')
            tel = request.POST.get('whatsapp')
            mail = request.POST.get('email')

            
            instance_personnel = Personnel.objects.get(id=personnel_id)

           
            instance_personnel.nom = nom
            instance_personnel.nationalite = nationalite
            instance_personnel.pays = country
            instance_personnel.parcours_meal = parcours_meal
            instance_personnel.fonction = fonction
            instance_personnel.tel = tel
            instance_personnel.mail = mail

            
            if request.FILES.get('photo'):
                instance_personnel.photo = request.FILES.get('photo')

            instance_personnel.save()

            

           
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect(request.META.get('HTTP_REFERER','/'))  # Remplacez 'profile' par l'URL de la page de profil

        except ObjectDoesNotExist:
            # Si l'objet Personnel n'existe pas, afficher un message d'erreur
            messages.error(request, "Le profil demandé n'existe pas.")
            return redirect(request.META.get('HTTP_REFERER','/'))  # Ou toute autre page de votre choix

        except Exception as e:
            # Gérer toute autre exception (par exemple des erreurs liées à la base de données)
            messages.error(request, f"Une erreur s'est produite : {str(e)}")
            return redirect(request.META.get('HTTP_REFERER','/'))

    # Si la méthode n'est pas POST, on redirige vers la page de profil ou la page d'édition
    return redirect(request.META.get('HTTP_REFERER','/'))  # Remplacez par l'URL d'édition du profil


def myCard(request):

    user_id = request.session.get('identification_user')
    if user_id:
        personnel = Personnel.objects.filter(bd_user = user_id).first()

        context={
        'personnel':personnel
        }
    else:
        return HttpResponse('donnee obselete')
    template = 'webpages/carte-adhesion.html'
    return render(request, template, context)

def count_male_and_female(request):
    data = Personnel.objects.aggregate(
        male=Count('id', filter=Q(sexe='H')),
        female=Count('id', filter=Q(sexe='F'))
    )

    return JsonResponse(data)


def group_member_by_country(request):
    # Comptage des membres par code pays (alpha_2)
    personnel = Personnel.objects.filter(country__isnull=False)\
        .values('country')\
        .annotate(total=Count('id'))

    results = {}
    for data in personnel:
        alpha2 = data['country'].lower() 
        try:
            country_info = pycountry.countries.get(alpha_2=alpha2.upper())
            if country_info:
                num_code = country_info.numeric.zfill(3)
                results[num_code] = {
                    'total': data['total'],
                    'flag_code': alpha2,          
                    'name': country_info.name       
                }
        except Exception as e:
           
            continue

    return JsonResponse(results)




def memberscountry(request, country):
    template = 'webpages/details-country.html'
    
    country_upper = country.upper()
    
    # --- Récupération du nom complet ---
    # Recherche le pays par son code (alpha_2)
    country_obj = pycountry.countries.get(alpha_2=country_upper)
    # Si trouvé, on prend le nom, sinon on garde le code
    country_name = country_obj.name if country_obj else country_upper
    
    country_members = Personnel.objects.filter(country=country_upper)
    country_members_female = country_members.filter(sexe="F").count()
    country_members_male = country_members.filter(sexe="H").count()
    
    context = {
        'members_count': country_members.count(),
        'member': country_members,
        'pays_code': country_upper,       # Le code (ex: FR)
        'pays_nom': country_name,         # Le nom complet (ex: France)
        'country_members_female': country_members_female,
        'country_members_male': country_members_male
    }
    
    return render(request, template, context)


def ProfilExpert(request):
    code_personnel = request.session.get('personnel_code')
    
    expert = Personnel.objects.get(code=code_personnel)
    context = {
        'expert': expert,
        
        'xs_extra': construire_xs_extra(expert),
    }
    if expert.cartographie_is_valid:
        return render(request, 'webpages/profil_expert.html', context)
    return render(request, 'webpages/cartographie.html', context)


def construire_xs_extra(expert):
    """Retourne {} tant que les modèles correspondants n'existent pas : aucune section n'apparaît."""
    extra = {}

   
    return extra

import json
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email, URLValidator
from cities_light.models import Country as CitiesLightCountry, City as CitiesLightCity
import logging
logger = logging.getLogger(__name__)

def secure_create_or_update_personnel(request):
    if request.method != 'POST':
        return JsonResponse({'error': "Méthode non autorisée."}, status=405)

    # 1. PARSING ROBUSTE DE LA REQUÊTE (JSON ou Form-Data)
    post_data = {}
    if request.content_type == 'application/json' or request.body:
        try:
            post_data = json.loads(request.body)
        except json.JSONDecodeError:
            post_data = request.POST.dict()
    
    if not post_data and request.POST:
        post_data = request.POST.dict()

    # Fonction utilitaire pour extraire proprement les listes
    def get_as_list(*keys):
        for key in keys:
            val = post_data.get(key)
            if val is not None:
                if isinstance(val, list):
                    return val
                if isinstance(val, str) and val.strip():
                    return [v.strip() for v in val.split(',') if v.strip()]
                return [val]
        return []

    # Détection des tables associées présentes dans le payload
    has_profils = 'profils' in post_data or 'profils[]' in post_data
    has_domaines = 'domaines' in post_data or 'domaines[]' in post_data
    has_secteurs = 'secteurs' in post_data or 'secteurs[]' in post_data
    has_outils = 'outils' in post_data or 'outils[]' in post_data
    has_dispo = 'dispo' in post_data or 'dispo[]' in post_data

    # Extraction des listes d'IDs
    profils_ids = get_as_list('profils', 'profils[]', 'profil', 'profil_ids')
    domaines_ids = get_as_list('domaines', 'domaines[]', 'domaine', 'domaine_ids')
    secteurs_ids = get_as_list('secteurs', 'secteurs[]', 'secteur', 'secteur_intervention')
    outils_ids = get_as_list('outils', 'outils[]', 'outil', 'outils_meal')
    disponibilites_ids = get_as_list('dispo', 'dispo[]', 'disponibilites', 'disponibilité')

    # Extraction des expériences par profil
    profils_experiences = {}
    if isinstance(post_data, dict):
        if isinstance(post_data.get('profils_experiences'), dict):
            profils_experiences = post_data.get('profils_experiences')
        else:
            for key, value in post_data.items():
                if str(key).startswith('experience_'):
                    p_id = str(key).split('_')[1]
                    profils_experiences[p_id] = value

    # Identification unique de l'utilisateur par e-mail ou session
    lookup_value = post_data.get('email') or post_data.get('mail')
    if not lookup_value:
        personnel_code = request.session.get('personnel_code')
        if personnel_code:
            try:
                p_obj = Personnel.objects.get(code=personnel_code)
                lookup_value = p_obj.mail
            except Personnel.DoesNotExist:
                pass

    if not lookup_value:
        return JsonResponse({'errors': {'email': "L'adresse e-mail est obligatoire pour l'enregistrement."}}, status=400)

    # 2. VALIDATIONS
    try:
        validate_email(lookup_value)
    except DjangoValidationError:
        return JsonResponse({'errors': {'email': "Format d'adresse e-mail invalide."}}, status=400)

    linkedin_url = post_data.get('linkedin') or post_data.get('profil_linkedin')
    if linkedin_url:
        validator = URLValidator()
        try:
            validator(linkedin_url)
        except DjangoValidationError:
            return JsonResponse({'errors': {'linkedin': "L'URL du profil LinkedIn est invalide."}}, status=400)

    # --- GESTION DU PAYS ET DES COORDONNÉES GÉOGRAPHIQUES ---
    pays_input = post_data.get('pays') or post_data.get('country')
    resolved_pays = None
    country_longitude = None
    country_latitude = None

    if pays_input is not None:
        resolved_pays = str(pays_input).strip()
        try:
            if str(pays_input).isdigit():
                country_obj = CitiesLightCountry.objects.get(id=int(pays_input))
            else:
                country_obj = CitiesLightCountry.objects.get(name__iexact=str(pays_input).strip())
            resolved_pays = country_obj.name
        except CitiesLightCountry.DoesNotExist:
            pass

    ville_input = post_data.get('ville')
    if ville_input is not None:
        try:
            city_obj = CitiesLightCity.objects.filter(name__iexact=str(ville_input).strip()).first()
            if city_obj:
                if city_obj.longitude is not None:
                    country_longitude = int(round(float(city_obj.longitude)))
                if city_obj.latitude is not None:
                    country_latitude = int(round(float(city_obj.latitude)))
        except Exception as e:
            logger.warning(f"Erreur géolocalisation ville : {e}")

    # 3. CONSTRUCTION DYNAMIQUE DES CHAMPS À METTRE À JOUR
    update_fields = {}

    if 'nomComplet' in post_data or 'nom' in post_data:
        update_fields['nom'] = str(post_data.get('nomComplet', '') or post_data.get('nom', '')).strip()
    
    if 'prenom' in post_data:
        update_fields['prenom'] = str(post_data.get('prenom', '')).strip()

    update_fields['mail'] = str(lookup_value).strip()

    if 'telephone' in post_data or 'tel' in post_data:
        update_fields['tel'] = str(post_data.get('telephone', '') or post_data.get('tel', '')).strip()

    if resolved_pays is not None:
        update_fields['pays'] = resolved_pays
        update_fields['country'] = resolved_pays

    if ville_input is not None:
        update_fields['ville'] = str(ville_input).strip()
        lat_val = post_data.get('lattitude') or post_data.get('latitude')
        lon_val = post_data.get('longitude')
        
        if country_latitude is not None:
            update_fields['lattitude'] = country_latitude
        elif lat_val is not None and str(lat_val).isdigit():
            update_fields['lattitude'] = int(lat_val)

        if country_longitude is not None:
            update_fields['longitude'] = country_longitude
        elif lon_val is not None and str(lon_val).isdigit():
            update_fields['longitude'] = int(lon_val)

    if 'sexe' in post_data:
        update_fields['sexe'] = str(post_data.get('sexe', '')).strip()

    if linkedin_url is not None:
        update_fields['profil_linkedin'] = str(linkedin_url).strip()

    if 'typeOrg' in post_data or 'organization_type' in post_data:
        update_fields['organization_type'] = str(post_data.get('typeOrg', '') or post_data.get('organization_type', '')).strip()

    if 'fonctionOrg' in post_data or 'fonction_organization' in post_data:
        update_fields['fonction_organization'] = str(post_data.get('fonctionOrg', '') or post_data.get('fonction_organization', '')).strip()

    if 'bio' in post_data:
        update_fields['bio'] = str(post_data.get('bio', '')).strip()

    if 'consentement' in post_data:
        update_fields['consentement'] = bool(post_data.get('consentement', False))

    update_fields['cartographie_is_valid'] = True

    # --- PROFIL ACTUEL & EXPERTISE ---
    curr_prof = post_data.get('profil_actuel') or post_data.get('current_profil')
    if curr_prof is not None:
        update_fields['current_profil_id'] = int(curr_prof) if str(curr_prof).isdigit() else None

    annees_exp = post_data.get('annees_profil_actuel') or post_data.get('years_expertise')
    if annees_exp is not None:
        update_fields['years_expertise'] = int(annees_exp) if str(annees_exp).isdigit() else None
        
    if 'niveau_expertise' in post_data or 'level_expertise' in post_data:
        update_fields['level_expertise'] = str(post_data.get('niveau_expertise', '') or post_data.get('level_expertise', '')).strip()

    # --- TRAITEMENT EXPLICITE DES LANGUES DE TRAVAIL ---
    if 'is_speeck_french' in post_data:
        val_fr = post_data.get('is_speeck_french')
        update_fields['is_speeck_french'] = True if val_fr in [True, 'true', 'True', 1, '1', 'on'] else False

    if 'is_speeck_english' in post_data:
        val_en = post_data.get('is_speeck_english')
        update_fields['is_speeck_english'] = True if val_en in [True, 'true', 'True', 1, '1', 'on'] else False

    if 'langues_autres' in post_data or 'langues_autres[]' in post_data or 'other_language' in post_data:
        autres_list = get_as_list('langues_autres', 'langues_autres[]')
        if post_data.get('other_language'):
            autres_list.append(str(post_data.get('other_language')).strip())
        update_fields['other_language'] = ", ".join(list(set(filter(None, autres_list))))

    # Nettoyage : filtre les chaînes vides mais CONSERVE explicitement les booléens (True/False)
    update_fields = {
        k: v for k, v in update_fields.items() 
        if (v != "" and v is not None) or isinstance(v, bool)
    }

    # 4. VÉRIFICATION DES CLÉS ÉTRANGÈRES
    def verify_existence(model_class, ids_list):
        if ids_list:
            try:
                int_ids = [int(i) for i in ids_list if str(i).isdigit()]
            except (ValueError, TypeError):
                return []
            return list(model_class.objects.filter(id__in=int_ids).values_list('id', flat=True))
        return []

    verified_profils_ids = verify_existence(ProfilMeal, profils_ids)
    verified_domaines_ids = verify_existence(DomaineExpertise, domaines_ids)
    verified_secteurs_ids = verify_existence(SecteurIntervention, secteurs_ids)
    verified_outils_ids = verify_existence(OutilsMeal, outils_ids)
    verified_dispo_ids = verify_existence(DisponibilityType, disponibilites_ids)

    # 5. EXECUTION ATOMIQUE EN BASE DE DONNÉES
    try:
        with transaction.atomic():
            personnel, created = Personnel.objects.get_or_create(
                mail=lookup_value,
                defaults=update_fields
            )
            
            if not created:
                for key, value in update_fields.items():
                    setattr(personnel, key, value)
                personnel.save()

            # --- ProfilPersonnel ---
            if has_profils:
                old_experiences = {
                    item.profil_id: item.year_experience 
                    for item in ProfilPersonnel.objects.filter(personnel=personnel)
                }

                ProfilPersonnel.objects.filter(personnel=personnel).delete()
                
                if verified_profils_ids:
                    profil_objects = []
                    for p_id in verified_profils_ids:
                        exp_val = None
                        if isinstance(profils_experiences, dict):
                            exp_val = profils_experiences.get(str(p_id)) or profils_experiences.get(p_id)
                        if exp_val is None and f"experience_{p_id}" in post_data:
                            exp_val = post_data.get(f"experience_{p_id}")

                        exp_int = int(exp_val) if exp_val not in [None, ''] and str(exp_val).isdigit() else None

                        # Protection anti-écrasement si l'expérience existe déjà
                        if exp_int is None and p_id in old_experiences:
                            exp_int = old_experiences[p_id]

                        profil_objects.append(
                            ProfilPersonnel(
                                personnel=personnel,
                                profil_id=p_id,
                                year_experience=exp_int
                            )
                        )
                    ProfilPersonnel.objects.bulk_create(profil_objects)

            # --- PersonnelDomaine ---
            if has_domaines:
                PersonnelDomaine.objects.filter(personnel=personnel).delete()
                if verified_domaines_ids:
                    PersonnelDomaine.objects.bulk_create([
                        PersonnelDomaine(personnel=personnel, domaine_id=d_id) for d_id in verified_domaines_ids
                    ])

            # --- PersonnelSecteurIntervention ---
            if has_secteurs:
                PersonnelSecteurIntervention.objects.filter(personnel=personnel).delete()
                if verified_secteurs_ids:
                    PersonnelSecteurIntervention.objects.bulk_create([
                        PersonnelSecteurIntervention(personnel=personnel, secteur_intervention_id=s_id) for s_id in verified_secteurs_ids
                    ])

            # --- PersonnelOutilMeal ---
            if has_outils:
                PersonnelOutilMeal.objects.filter(personnel=personnel).delete()
                if verified_outils_ids:
                    PersonnelOutilMeal.objects.bulk_create([
                        PersonnelOutilMeal(personnel=personnel, outil_meal_id=o_id) for o_id in verified_outils_ids
                    ])

            # --- PersonnelDisponibilityType ---
            if has_dispo:
                PersonnelDisponibilityType.objects.filter(personnel=personnel).delete()
                if verified_dispo_ids:
                    PersonnelDisponibilityType.objects.bulk_create([
                        PersonnelDisponibilityType(personnel=personnel, type_disponibilite_id=dt_id) for dt_id in verified_dispo_ids
                    ])

        action_type = "Création" if created else "Mise à jour"
        return JsonResponse({
            'success': True,
            'message': f"Enregistrement effectué avec succès ({action_type}).",
        }, status=200)

    except Exception as e:
        logger.error(f"Erreur critique lors de l'enregistrement : {str(e)}")
        return JsonResponse({'error': f"Une erreur interne est survenue : {str(e)}"}, status=500)
def authentification(request):
    return render(request, 'webpages/login.html')


import random
from django.core.mail import send_mail as django_send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)

def VerificationEmailUser(request):
    """Étape 1 : Vérifie l'éligibilité de l'administrateur et génère l'OTP."""
    if request.method != 'POST':
        return JsonResponse({'error': "Méthode non autorisée."}, status=405)

    # 1. Parsing robuste du corps de la requête (JSON ou Form-Data)
    try:
        if request.content_type == 'application/json' or request.body:
            data = json.loads(request.body)
            email = str(data.get('email', '')).strip()
        else:
            email = str(request.POST.get('email', '')).strip()
    except json.JSONDecodeError:
        email = str(request.POST.get('email', '')).strip()

    if not email:
        return JsonResponse({'error': "L'adresse e-mail est requise."}, status=400)

    # 2. Vérification sécurisée via l'ORM (Protégé contre les injections SQL)
    user = User.objects.filter(is_superuser=True).filter(
        email__iexact=email
    ).first() or User.objects.filter(is_superuser=True, username__iexact=email).first()

    if not user or not user.email:
        return JsonResponse({'error': "Cet e-mail n'a pas d'accès administrateur valide."}, status=403)

    # 3. Génération du code OTP à 6 chiffres et de son expiration (10 minutes)
    code = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=10)

    # 4. Stockage sécurisé dans la session Django
    request.session['verification_code'] = code
    request.session['code_expires_at'] = expires_at.timestamp()
    request.session['verification_email'] = email
    request.session['admin_user_id'] = user.id

    # 5. Envoi de l'e-mail de vérification (Arguments positionnels sécurisés)
    try:
        django_send_mail(
            'Votre code de vérification administrateur - ADMIN',
            f'Bonjour,\n\nVotre code de vérification est : {code}.\nIl est valide pendant 10 minutes.\n\nMEAL AFRIQUE',
            None,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Erreur d'envoi d'e-mail OTP admin : {str(e)}")
        return JsonResponse({'error': f"Erreur lors de l'envoi de l'e-mail : {str(e)}"}, status=500)

    return JsonResponse({
        'sent': True, 
        'message': "Code de vérification envoyé avec succès à votre adresse administrateur."
    }, status=200)

def VerifyCodeUser(request):
    """Étape 2 : Vérifie le code OTP et connecte l'utilisateur."""
    if request.method != 'POST':
        return JsonResponse({'error': "Méthode non autorisée."}, status=405)

    try:
        data = json.loads(request.body)
        code_saisi = str(data.get('code', '')).strip()
    except json.JSONDecodeError:
        code_saisi = str(request.POST.get('code', '')).strip()

    # Récupération des données en session
    session_code = request.session.get('verification_code')
    expires_at_timestamp = request.session.get('code_expires_at')
    user_id = request.session.get('admin_user_id')

    if not session_code or not expires_at_timestamp or not user_id:
        return JsonResponse({'error': "Aucune session de vérification active. Veuillez demander un nouveau code."}, status=400)

    # 1. Vérification de l'expiration du code
    current_timestamp = timezone.now().timestamp()
    if current_timestamp > expires_at_timestamp:
        return JsonResponse({'error': "Ce code a expiré. Demandez-en un nouveau."}, status=410)

    # 2. Vérification de la correspondance du code
    if code_saisi != str(session_code):
        return JsonResponse({'error': "Code incorrect. Vérifiez et réessayez."}, status=400)

    # 3. Authentification et connexion de l'utilisateur
    try:
        user = User.objects.get(id=user_id, is_superuser=True)
        login(request, user)  # Crée la session d'authentification Django

        # Nettoyage des variables OTP en session
        del request.session['verification_code']
        del request.session['code_expires_at']
        del request.session['verification_email']
        del request.session['admin_user_id']

        return JsonResponse({
            'ok': True,
            'redirect': '/admin-dashboard/'  # Adaptez l'URL de redirection si nécessaire
        }, status=200)

    except User.DoesNotExist:
        return JsonResponse({'error': "Utilisateur introuvable."}, status=404)


from django.utils import timezone

def ValiderCodeView(request):
    if request.method == 'POST':
        user_code = request.POST.get('code')
        
        saved_code = request.session.get('verification_code')
        expires_at_timestamp = request.session.get('code_expires_at')
        
        if not saved_code or not expires_at_timestamp:
            # Aucun code trouvé ou déjà utilisé/expiré
            return render(request, 'erreur.html', {'message': "Aucun code en cours. Veuillez recommencer."})
            
        # Vérifier si le temps est dépassé
        if timezone.now().timestamp() > expires_at_timestamp:
            # Nettoyer la session
            del request.session['verification_code']
            del request.session['code_expires_at']
            return render(request, 'erreur.html', {'message': "Le code a expiré."})
            
        # Vérifier si le code est correct
        if user_code == saved_code:
            # Succès ! Nettoyer la session et connecter l'utilisateur ou le laisser continuer
            del request.session['verification_code']
            del request.session['code_expires_at']
            return JsonResponse({'success: user_code'})
        else:
            print("Code incorrect")
            
    return render(request, 'webpages/login.html')


def dashboard(request):

    return render(request, 'webpages/dashboard.html')


def VerificationCodeUser(request):
    personnel = request.session.get('verification_code')

    return render(request, 'webpages/verification-code-user.html')


def mask_email(email):
    """ Masque l'email pour l'affichage (ex: j***n@example.com) """
    if not email or '@' not in email:
        return email
    username, domain = email.split('@', 1)
    if len(username) <= 2:
        masked_user = username[0] + "*"
    else:
        masked_user = username[0] + "*" * (len(username) - 2) + username[-1]
    return f"{masked_user}@{domain}"


def verification_otp_view(request):
    # 1. Sécurité : Vérifier qu'un email est bien en session
    email = request.session.get('otp_email')
    if not email:
        messages.error(request, "Session expirée ou invalide. Veuillez saisir votre email.")
        return redirect('check_email_page')

    personne = Personnel.objects.filter(mail=email).first()
    if not personne:
        messages.error(request, "Utilisateur introuvable.")
        return redirect('check_email_page')

    # 2. Traitement des soumissions POST (Vérification ou Renvoi)
    if request.method == "POST":
        action = request.POST.get('action')

        # --- CAS A : SOUMISSION DU CODE OTP ---
        if action == "verify":
            code_saisi = request.POST.get('otp', '').strip()

            if len(code_saisi) != 6 or not code_saisi.isdigit():
                messages.error(request, "Le code doit contenir exactement 6 chiffres.")
            else:
                try:
                    otp_obj = OtpPersonnel.objects.get(
                        personnel=personne,
                        code=code_saisi,
                        is_used=False
                    )


                    # Vérification de la durée de validité (ex: 5 min)
                    if timezone.now() > otp_obj.expires_at:
                        messages.error(request, "Ce code OTP a expiré. Veuillez en demander un nouveau.")
                    else:
                        # Validation réussie
                        otp_obj.is_used = True
                        otp_obj.save()

                        # Nettoyage de la variable temporaire de session
                        del request.session['otp_email']

                        # Authentification de l'utilisateur / création de la session de connexion
                        request.session['personnel_code'] = personne.code
                        messages.success(request, "Authentification réussie ! Bienvenue.")
                        return redirect('/Information-members/')  # Rediriger vers la page d'accueil/tableau de bord

                except OtpPersonnel.DoesNotExist:
                    messages.error(request, "Code OTP incorrect.")

        # --- CAS B : RENVOI DU CODE OTP ---
        elif action == "resend":
            # Générer un nouveau code OTP
            nouveau_code = f"{random.randint(0, 999999):06d}"
            expiration = timezone.now() + datetime.timedelta(minutes=5)

            # Invalider les anciens codes
            OtpPersonnel.objects.filter(personnel=personne, is_used=False).update(is_used=True)

            # Créer le nouveau code
            OtpPersonnel.objects.create(
                personnel=personne,
                code=nouveau_code,
                expires_at=expiration
            )

            # Envoyer l'e-mail
            nom_personnel = getattr(personne, 'nom', 'Utilisateur')
            send_mail(
                subject="Votre nouveau code de vérification OTP",
                message=f"Bonjour {nom_personnel},\n\nVotre nouveau code OTP est : {nouveau_code}\n\nIl expire dans 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Un nouveau code OTP vient de vous être envoyé par e-mail.")

    # 3. Préparation des données du contexte pour le template HTML
    context = {
        'email_masque': mask_email(email),
        'delai_renvoi': 60,  # Déclenche le compte à rebours de 60s du JS
    }

    return render(request, 'webpages/verification-code-user.html', context)



def deconnexion_view(request):
    # La fonction logout() s'occupe de tout détruire proprement
    logout(request)
    
    # Rediriger l'utilisateur vers la page de connexion par OTP
    return redirect('/Inscription-meal-afrique/') # ou l'URL de votre page d'accueil/connexion


def send_mail(request):
    return render(request, 'webpages/emails/group_mail.html')



def actualite(request):
    return render(request, 'webpages/actualites/actualite-form.html')


def logout_admin(request):
    logout(request)
    return redirect('/')