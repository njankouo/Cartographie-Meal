from django.shortcuts import render
from django_countries import countries
from .models import *
from django.db.models import Count, Q
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_expert_registration_email
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


logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'webpages/index.html')


def MealAfrique(request):
    # Total du personnel
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
        'countries': countries,
    }

    return render(request, 'webpages/inscription.html', context)

def CountMembers(request):
    personnel = Personnel.objects.count()
    return JsonResponse({'personnel':personnel})


@csrf_exempt  
def check_email_ajax(request):
    if request.method == "POST":
        import json
        try:
            data = json.loads(request.body)
            email = data.get("email", "").strip()
        except json.JSONDecodeError:
            return JsonResponse({"exists": False, "error": "Données invalides"})

        if not email:
            return JsonResponse({"exists": False, "error": "Email vide"})

        try:
            personne = Personnel.objects.filter(mail=email).first()
            
            return JsonResponse({"exists": True, "code": personne.code})
        except Personnel.DoesNotExist:
            return JsonResponse({"exists": False})

    return JsonResponse({"exists": False, "error": "Méthode non autorisée"})



# On récupère les logs pour voir les erreurs dans ton terminal
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


def Information_members(request, code):
    template = 'webpages/infos-member.html'

    personnel = get_object_or_404(Personnel, code=code)

    context ={
    'personnel':personnel
    }

    return render(request, template, context)

from cities_light.models import City, Country

def Cartographie(request, code):
    personnel = Personnel.objects.get(code=code)
    
    # Récupérer tous les pays de cities-light triés par nom
    countries = Country.objects.all().order_by('name')

    context = {
        'countries': countries,
        'personnel': personnel,
        'domaine_expertise':DomaineExpertise.objects.all(),
        'profils':ProfilMeal.objects.all(),
        'secteurs':SecteurIntervention.objects.all(),
        'outils':OutilsMeal.objects.all(),
        'types_disponibilite':DisponibilityType.objects.all()
    }
    chec_verification_cartographie = personnel.cartographie_is_valid

    if chec_verification_cartographie:
        return  render(request, 'webpages/profil_expert.html', context)
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

def EditProfil(request, code):
    template = 'webpages/edit-profil.html'

    personnel = Personnel.objects.get(code=code)

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
            return redirect(f'/Information-members/{instance_personnel.code}/')  # Remplacez 'profile' par l'URL de la page de profil

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


def ProfilExpert(request, code):
    personnel = Personnel.objects.get(code=code)
    context ={
        'personnel':personnel
    }
    return render(request, 'webpages/profil_expert.html', context)




def secure_create_or_update_personnel(data: dict, unique_field='code'):
 
    
    # 1. EXTRACTION ET NETTOYAGE DES RELATIONS
    domaines_ids = data.pop('domaines', None)
    secteurs_ids = data.pop('secteurs_intervention', None)
    outils_ids = data.pop('outils_meal', None)
    disponibilites_ids = data.pop('types_disponibilite', None)
    year_experience_profil = data.pop('year_experience_profil', None)

    # Vérification du champ unique de recherche
    lookup_value = data.get(unique_field)
    if not lookup_value:
        raise ValidationError({unique_field: f"Le champ de recherche '{unique_field}' est obligatoire."})

    # 2. VALIDATION STRICTE DES DONNÉES (DATA INTEGRITY & FORMATS)
    
    # Validation de l'e-mail si présent
    if data.get('mail'):
        try:
            validate_email(data['mail'])
        except DjangoValidationError:
            raise ValidationError({'mail': "Format d'adresse e-mail invalide."})

    # Validation du profil LinkedIn si présent
    if data.get('profil_linkedin'):
        validator = URLValidator()
        try:
            validator(data['profil_linkedin'])
        except DjangoValidationError:
            raise ValidationError({'profil_linkedin': "L'URL du profil LinkedIn est invalide."})

    # Nettoyage de base des chaînes textuelles (protection contre les espaces superflus)
    for field in ['nom', 'prenom', 'fonction', 'code']:
        if data.get(field):
            data[field] = str(data[field]).strip()

    # 3. VÉRIFICATION DE L'EXISTENCE DES CLÉS ÉTRANGÈRES (Empêche l'injection d'IDs corrompus ou orphelins)
    if data.get('current_profil'):
        profil_id = data['current_profil'].id if hasattr(data['current_profil'], 'id') else data['current_profil']
        if not ProfilMeal.objects.filter(id=profil_id).exists():
            raise ValidationError({'current_profil': "Le profil MEAL spécifié n'existe pas en base de données."})

    def verify_existence(model_class, ids_list, field_name):
        if ids_list:
            # S'assure que tous les IDs fournis existent réellement et gère les doublons potentiels
            existing_count = model_class.objects.filter(id__in=ids_list).count()
            if existing_count != len(set(ids_list)):
                raise ValidationError({field_name: "Un ou plusieurs identifiants fournis n'existent pas."})

    verify_existence(DomaineExpertise, domaines_ids, 'domaines')
    verify_existence(SecteurIntervention, secteurs_ids, 'secteurs_intervention')
    verify_existence(OutilsMeal, outils_ids, 'outils_meal')
    verify_existence(DisponibilityType, disponibilites_ids, 'types_disponibilite')

    # 4. EXÉCUTION SÉCURISÉE EN TRANSACTION ATOMIQUE (Règle ACID)
    try:
        with transaction.atomic():
            lookup_kwargs = {unique_field: lookup_value}
            personnel, created = Personnel.update_or_create(
                **lookup_kwargs,
                defaults=data
            )

            # Gestion de la table ProfilPersonnel
            if personnel.current_profil:
                ProfilPersonnel.objects.update_or_create(
                    personnel=personnel,
                    profil=personnel.current_profil,
                    defaults={'year_experience': year_experience_profil}
                )

            # Synchronisation sécurisée des relations Many-to-Many / Intermédiaires
            if domaines_ids is not None:
                PersonnelDomaine.objects.filter(personnel=personnel).delete()
                PersonnelDomaine.objects.bulk_create([
                    PersonnelDomaine(personnel=personnel, domaine_id=d_id) for d_id in domaines_ids
                ])

            if secteurs_ids is not None:
                PersonnelSecteurIntervention.objects.filter(personnel=personnel).delete()
                PersonnelSecteurIntervention.objects.bulk_create([
                    PersonnelSecteurIntervention(personnel=personnel, secteur_intervention_id=s_id) for s_id in secteurs_ids
                ])

            if outils_ids is not None:
                PersonnelOutilMeal.objects.filter(personnel=personnel).delete()
                PersonnelOutilMeal.objects.bulk_create([
                    PersonnelOutilMeal(personnel=personnel, outil_meal_id=o_id) for o_id in outils_ids
                ])

            if disponibilites_ids is not None:
                PersonnelDisponibilityType.objects.filter(personnel=personnel).delete()
                PersonnelDisponibilityType.objects.bulk_create([
                    PersonnelDisponibilityType(personnel=personnel, type_disponibilite_id=dt_id) for dt_id in disponibilites_ids
                ])

        # 5. TRAÇABILITÉ (AUDIT LOG SYSTÈME)
        action_type = "Création" if created else "Mise à jour"
        logger.info(f"Sécurité - {action_type} réussie du personnel (Code: {personnel.code}) par le processus système.")

        return personnel, created

    except Exception as e:
        logger.error(f"Erreur critique lors du create_update sécurisé du personnel : {str(e)}")
        raise e