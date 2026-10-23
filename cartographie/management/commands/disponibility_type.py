from cartographie.models import DisponibilityType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Charge ou met à jour la liste complète des types de disponibilité"

    def handle(self, *args, **kwargs):
        TYPES_DISPONIBILITE = [
            # 1. Emploi & Salariat
            {
                "code": "DISP-EMP-CDI",
                "intitule": "Emploi direct (CDI / Temps plein)",
                "fr": "Engagement à temps plein sur la durée dans le cadre d'un contrat à durée indéterminée.",
            },
            {
                "code": "DISP-EMP-CDD",
                "intitule": "Emploi direct (CDD / Mission court-moyen terme)",
                "fr": "Engagement salarié à durée déterminée pour la durée d'un projet ou d'un remplacement.",
            },
            {
                "code": "DISP-EMP-PART",
                "intitule": "Emploi à temps partiel / Mi-temps",
                "fr": "Disponibilité pour un emploi salarié avec un volume horaire réduit.",
            },

            # 2. Consultance & Expertise Indépendante
            {
                "code": "DISP-CONS-COURT",
                "intitule": "Consultance de courte durée (Missions ponctuelles)",
                "fr": "Interventions rapides, audits, évaluations à mi-parcours/finales ou appuis techniques ponctuels.",
            },
            {
                "code": "DISP-CONS-LONG",
                "intitule": "Consultance long terme / Accord-cadre",
                "fr": "Accompagnement d'expertise sur plusieurs mois, contrat-cadre ou assistance technique résidente.",
            },

            # 3. Formation, Renforcement de capacités & Animation
            {
                "code": "DISP-FORM",
                "intitule": "Formation / Facilitation",
                "fr": "Conception et animation de modules de formation, ateliers participatifs et facilitation de groupes de travail.",
            },
            {
                "code": "DISP-MENT",
                "intitule": "Mentorat / Coaching",
                "fr": "Accompagnement personnalisé, coaching d'équipe, parrainage et transfert progressif de compétences.",
            },

            # 4. Recherche, Publication & Analyse
            {
                "code": "DISP-RECH",
                "intitule": "Recherche / Publication / Études",
                "fr": "Conduite de travaux de recherche, rédaction de rapports analytiques, d'articles scientifiques ou d'ouvrages.",
            },

            # 5. Partenariats, Réseaux & Bénévolat
            {
                "code": "DISP-PART",
                "intitule": "Partenariat / Projet conjoint",
                "fr": "Collaboration entre organisations, consortiums, co-conception de projets et partenariats stratégiques.",
            },
            {
                "code": "DISP-BENEVOLAT",
                "intitule": "Bénévolat / Pro Bono",
                "fr": "Appui technique à titre gracieux pour soutenir des causes sociales ou des organisations émergentes.",
            },

            # 6. Modes d'Intervention d'Urgence & Mobilité
            {
                "code": "DISP-URGENCE",
                "intitule": "Déploiement d'urgence / Surge Capacity",
                "fr": "Disponibilité immédiate sous 24-48h pour un déploiement sur le terrain en contexte de crise.",
            },
            {
                "code": "DISP-REMOTE",
                "intitule": "Support à distance / Télétravail exclusif",
                "fr": "Disponibilité pour des missions réalisées intégralement à distance (remote context).",
            },

            # 7. Autres
            {
                "code": "DISP-AUTRE",
                "intitule": "Autre (précisez)",
                "fr": "Autres formes spécifiques d'engagement ou de disponibilité.",
            },
        ]

        count = 0
        for item in TYPES_DISPONIBILITE:
            code = item["code"]

            disp_type, created = DisponibilityType.objects.update_or_create(
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
                f"\nChargement terminé avec succès ! ({count} types de disponibilité enregistrés)"
            )
        )