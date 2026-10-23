from cartographie.models import SecteurIntervention
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Charge ou met à jour la liste complète des secteurs d'intervention"

    def handle(self, *args, **kwargs):
        SECTEURS = [
            # 1. Humanitaire & Action d'Urgence
            {
                "code": "SECT-HUM",
                "intitule": "Humanitaire & Urgence",
                "fr": "Interventions d'urgence, assistance immédiate, gestion des crises, catastrophes naturelles et déplacements forcés.",
            },
            {
                "code": "SECT-PROT",
                "intitule": "Protection",
                "fr": "Protection des populations vulnérables, droits de l'enfant, violences basées sur le genre (VBG), protection juridique et assistance aux réfugiés/PDI.",
            },
            {
                "code": "SECT-MIGR",
                "intitule": "Migrations & Déplacements",
                "fr": "Gestion des flux migratoires, intégration, assistance aux déplacés internes et réfugiés.",
            },
            {
                "code": "SECT-MINES",
                "intitule": "Action contre les mines",
                "fr": "Dépollution pyrotechnique, déminage humanitaire, sensibilisation aux risques et assistance aux victimes.",
            },

            # 2. Santé, Nutrition & WASH
            {
                "code": "SECT-SANTE",
                "intitule": "Santé publique",
                "fr": "Renforcement des systèmes de santé, soins de santé primaires, santé maternelle et infantile, lutte contre les épidémies et pandémies.",
            },
            {
                "code": "SECT-SMENT",
                "intitule": "Santé mentale & Appui psychosocial",
                "fr": "Prise en charge de la santé mentale, soutien psychologique et traumatisme des populations affectées par les crises.",
            },
            {
                "code": "SECT-NUTR",
                "intitule": "Nutrition",
                "fr": "Prévention et traitement de la malnutrition aiguë et chronique, sécurité nutritionnelle.",
            },
            {
                "code": "SECT-WASH",
                "intitule": "Eau, Hygiène et Assainissement (WASH)",
                "fr": "Accès à l'eau potable, construction d'infrastructures sanitaires, gestion des déchets et promotion de l'hygiène.",
            },

            # 3. Agriculture, Alimentation & Moyen d'existence
            {
                "code": "SECT-AGRI",
                "intitule": "Agriculture & Élevage",
                "fr": "Soutien aux petits producteurs, développement des filières agricoles, pastoralisme, santé animale et durabilité.",
            },
            {
                "code": "SECT-SECALIM",
                "intitule": "Sécurité alimentaire",
                "fr": "Distribution alimentaire, transferts monétaires (Cash Transfer), résilience des moyens d'existence et souveraineté alimentaire.",
            },
            {
                "code": "SECT-PECHE",
                "intitule": "Pêche & Aquaculture",
                "fr": "Gestion durable de la pêche, développement de l'aquaculture et protection des écosystèmes aquatiques.",
            },

            # 4. Éducation, Emploi & Jeunesse
            {
                "code": "SECT-EDUC",
                "intitule": "Éducation",
                "fr": "Éducation formelle primaire, secondaire et supérieure, accès équitable et amélioration de la qualité de l'enseignement.",
            },
            {
                "code": "SECT-FORM",
                "intitule": "Formation professionnelle & Insertion",
                "fr": "Enseignement technique, développement des compétences professionnelles et apprentissage.",
            },
            {
                "code": "SECT-EMPLOI",
                "intitule": "Emploi & Entrepreneuriat",
                "fr": "Création d'emplois, soutien aux PME/TPE, entrepreneuriat des jeunes et des femmes, insertion socio-économique.",
            },
            {
                "code": "SECT-JEUNESSE",
                "intitule": "Jeunesse & Sports",
                "fr": "Autonomisation de la jeunesse, loisirs, civisme, culture et cohésion sociale par le sport.",
            },

            # 5. Gouvernance, Droits & Paix
            {
                "code": "SECT-GOUV",
                "intitule": "Gouvernance & Démocratie",
                "fr": "Appui institutionnel, transparence, lutte contre la corruption, processus électoraux et redevabilité publique.",
            },
            {
                "code": "SECT-JUSTICE",
                "intitule": "Justice & Droits humains",
                "fr": "Accès à la justice, État de droit, réforme judiciaire et défense des droits fondamentaux.",
            },
            {
                "code": "SECT-PAIX",
                "intitule": "Consolidation de la paix & Cohésion sociale",
                "fr": "Prévention des conflits, médiation, dialogue communautaire, réconciliation et prévention de l'extrémisme violent.",
            },
            {
                "code": "SECT-DECENTRALISATION",
                "intitule": "Décentralisation & Développement local",
                "fr": "Renforcement des collectivités locales, gouvernance territoriale et planification locale.",
            },

            # 6. Environnement, Climat & Énergie
            {
                "code": "SECT-ENV",
                "intitule": "Environnement & Biodiversité",
                "fr": "Protection des écosystèmes, préservation de la biodiversité, reboisement et lutte contre la désertification.",
            },
            {
                "code": "SECT-CLIMAT",
                "intitule": "Changement climatique & Résilience",
                "fr": "Adaptation et atténuation du changement climatique, réduction des risques de catastrophe (RRC).",
            },
            {
                "code": "SECT-ENERGIE",
                "intitule": "Énergie & Électrification",
                "fr": "Accès aux énergies renouvelables (solaire, éolien, etc.), efficacité énergétique et électrification rurale.",
            },

            # 7. Économie, Finance & Infrastructures
            {
                "code": "SECT-DEV",
                "intitule": "Développement économique",
                "fr": "Macroéconomie, commerce, intégration régionale et politiques économiques de développement.",
            },
            {
                "code": "SECT-MICROFINANCE",
                "intitule": "Inclusion financière & Microfinance",
                "fr": "Accès aux services financiers, tontines améliorées, épargne/crédit et éducation financière.",
            },
            {
                "code": "SECT-INFRA",
                "intitule": "Infrastructures & Transport",
                "fr": "Construction et réhabilitation de routes, ponts, bâtiments publics, pistes rurales et transports.",
            },
            {
                "code": "SECT-URBAIN",
                "intitule": "Développement urbain & Habitat",
                "fr": "Aménagement du territoire, gestion des villes, logement social et assainissement urbain.",
            },

            # 8. Transversal, Inclusion & Technologies
            {
                "code": "SECT-GENRE",
                "intitule": "Genre & Inclusion sociale",
                "fr": "Égalité des sexes, autonomisation des femmes, inclusion des personnes en situation de handicap et des minorités.",
            },
            {
                "code": "SECT-DIGITAL",
                "intitule": "Numérique & Technologies (ICT4D)",
                "fr": "Digitalisation des services, inclusion numérique, innovation technologique au service du développement.",
            },
            {
                "code": "SECT-CULTURE",
                "intitule": "Culture, Patrimoine & Tourisme",
                "fr": "Valorisation du patrimoine culturel, soutien aux industries créatives et tourisme durable.",
            },
            {
                "code": "SECT-AUTRE",
                "intitule": "Autre",
                "fr": "Secteurs d'intervention spécifiques non listés ci-dessus.",
            },
        ]

        count = 0
        for item in SECTEURS:
            code = item["code"]
            
            secteur, created = SecteurIntervention.objects.update_or_create(
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
                f"\nChargement terminé avec succès ! ({count} SecteurIntervention enregistrés au total)"
            )
        )