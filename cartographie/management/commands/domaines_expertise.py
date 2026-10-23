from cartographie.models import DomaineExpertise
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Charge ou met à jour l'ensemble des profils MEAL dans la base de données"

    def handle(self, *args, **kwargs):
        PROFILS = [
            {
                "code": "PMEAL-SUIVI",
                "intitule": "Suivi de projets",
                "fr": "Suivi régulier des activités, des indicateurs et de l'avancement des projets.",
            },
            {
                "code": "PMEAL-EVAL",
                "intitule": "Évaluation d'impact",
                "fr": "Évaluation des effets à moyen et long termes, analyses contrefactuelles et évaluations externes.",
            },
            {
                "code": "PMEAL-AAP",
                "intitule": "Redevabilité / AAP",
                "fr": "Redevabilité envers les populations affectées, mécanismes de rétroaction et participation communautaire.",
            },
            {
                "code": "PMEAL-APPRENTISSAGE",
                "intitule": "Apprentissage organisationnel",
                "fr": "Capitalisation des expériences, leçons apprises et partage des connaissances.",
            },
            {
                "code": "PMEAL-DIGITAL",
                "intitule": "Digitalisation MEAL",
                "fr": "Numérisation des processus de collecte, automatisation et tableaux de bord (PowerBI, Kobo, ODK, etc.).",
            },
            {
                "code": "PMEAL-GAR",
                "intitule": "Gestion axée sur les résultats",
                "fr": "Planification, suivi et pilotage axés sur les résultats et l'impact mesurable.",
            },
            {
                "code": "PMEAL-FINANCES",
                "intitule": "Finances publiques",
                "fr": "Suivi budgétaire, analyse financière et audit des programmes publics.",
            },
            {
                "code": "PMEAL-GENRE",
                "intitule": "Genre et inclusion",
                "fr": "Intégration transversale du genre, de l'équité et de l'inclusion des groupes vulnérables.",
            },
            {
                "code": "PMEAL-CADRELOG",
                "intitule": "Cadre logique / Théorie du changement",
                "fr": "Conception de cadres logiques, théories du changement et matrices d'indicateurs.",
            },
            # Domaines essentiels ajoutés
            {
                "code": "PMEAL-COLLECTE",
                "intitule": "Collecte de données & Enquêtes",
                "fr": "Conception d'outils, échantillonnage, enquêtes de référence (baseline), à mi-parcours et finales (endline).",
            },
            {
                "code": "PMEAL-MGP",
                "intitule": "Mécanisme de Gestion des Plaintes (MGP)",
                "fr": "Mise en place et gestion des canaux de rétroaction, plaintes et suggestions (CEA).",
            },
            {
                "code": "PMEAL-ANALYSE",
                "intitule": "Analyse de données & Statistiques",
                "fr": "Traitement statistique, analyse qualitative/quantitative et production de rapports analytiques.",
            },
            {
                "code": "PMEAL-AUTRE",
                "intitule": "Autre",
                "fr": "Autres domaines ou compétences spécifiques liés au MEAL.",
            },
        ]

        count = 0
        for item in PROFILS:
            code = item["code"]
            
            profil, created = DomaineExpertise.objects.update_or_create(
                code=code,
                defaults={
                    "intitule": item["intitule"],
                    "description": item["fr"],
                },
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Créé : {code}"))
            else:
                self.stdout.write(f"Mis à jour : {code}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nChargement terminé avec succès ! ({count} nouveaux DomaineExpertise enregistrés)"
            )
        )