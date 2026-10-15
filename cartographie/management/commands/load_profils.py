from cartographie.models import ProfilMeal
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Charge ou met à jour l'ensemble des profils MEAL dans la base de données"

    def handle(self, *args, **kwargs):
        PROFILS = [
            {
                "code": "PMEAL-Consultant",
                "fr": "Expert externe mobilisé pour la conception de systèmes MEAL, la conduite d'évaluations et d'études spécialisées, l'analyse de données et le renforcement des capacités.",
                "en": "External expert engaged for MEAL system design, evaluations and specialized studies, data analysis, and capacity building.",
            },
            {
                "code": "PMEAL-Accountability Officer",
                "fr": "Met en œuvre les mécanismes de redevabilité envers les populations affectées : gestion des plaintes et retours, participation communautaire, protection et approches transversales.",
                "en": "Implements accountability mechanisms toward affected populations: complaints and feedback management, community participation, protection and cross-cutting approaches.",
            },
            {
                "code": "PMEAL-Analyst",
                "fr": "Analyse les données quantitatives et qualitatives du programme, construit et interprète les indicateurs, produit des visualisations et appuie l'analyse des données d'évaluation.",
                "en": "Analyzes quantitative and qualitative program data, builds and interprets indicators, produces visualizations and supports evaluation data analysis.",
            },
            {
                "code": "PMEAL-BI Officer",
                "fr": "Conçoit les tableaux de bord et les systèmes de Business Intelligence du programme ; structure les bases de données et les flux d'information pour le pilotage et la prise de décision.",
                "en": "Designs program dashboards and Business Intelligence systems; structures databases and information flows for steering and decision-making.",
            },
            {
                "code": "PMEAL-Coordinator",
                "fr": "Coordonne et harmonise les pratiques, outils et standards MEAL entre plusieurs équipes, sites ou projets ; assure la qualité et la cohérence transversale du dispositif.",
                "en": "Coordinates and harmonizes MEAL practices, tools and standards across teams, sites or projects; ensures cross-cutting quality and consistency.",
            },
            {
                "code": "PMEAL-Data Officer",
                "fr": "Gère la collecte, la saisie, le nettoyage et la structuration des données MEAL ; assure la qualité et la sécurité des bases de données et l'usage des outils numériques de collecte.",
                "en": "Manages collection, entry, cleaning and structuring of MEAL data; ensures database quality and security and the use of digital collection tools.",
            },
            {
                "code": "PMEAL-Digital MEAL",
                "fr": "Pilote la transformation numérique du dispositif MEAL : sélection et déploiement des outils digitaux, architecture des systèmes d'information, automatisation et intégration de l'intelligence artificielle.",
                "en": "Leads the digital transformation of the MEAL system: selection and deployment of digital tools, information system architecture, automation and AI integration.",
            },
            {
                "code": "PMEAL-Head of MEAL",
                "fr": "Définit la stratégie et la gouvernance MEAL au niveau organisationnel ou pays : politique qualité, relations bailleurs, gestion d'équipe et culture de redevabilité et d'apprentissage.",
                "en": "Defines MEAL strategy and governance at organizational or country level: quality policy, donor relations, team management, and a culture of accountability and learning.",
            },
            {
                "code": "PMEAL-Learning Officer",
                "fr": "Anime la culture d'apprentissage organisationnel : capitalisation, gestion des connaissances, revues après action et diffusion des résultats pour l'amélioration continue des programmes.",
                "en": "Drives the organizational learning culture: capitalization, knowledge management, after-action reviews and dissemination of results for continuous program improvement.",
            },
            {
                "code": "PMEAL_MEAL Manager",
                "fr": "Pilote la conception et la mise en œuvre du système MEAL d'un projet ou programme et encadre l'équipe MEAL.",
                "en": "Leads the design and implementation of a project or program's MEAL system and supervises the MEAL team.",
            },
            {
                "code": "PMEAL-MEAL Officer",
                "fr": "Rôle généraliste de terrain couvrant l'ensemble des fonctions MEAL de premier niveau : collecte, suivi, redevabilité de base et appui aux évaluations et à l'apprentissage.",
                "en": "Generalist field role covering first-level MEAL functions: data collection, monitoring, basic accountability, and support to evaluations and learning.",
            },
            {
                "code": "PMEAL-Monitoring Officer",
                "fr": "Assure le suivi opérationnel de routine : visites de terrain, suivi des activités et des bénéficiaires, contrôle qualité des données collectées, alimentation des tableaux de bord.",
                "en": "Ensures routine operational monitoring: field visits, activity and beneficiary tracking, quality control of collected data, and dashboard feeding.",
            },
            {
                "code": "PMEAL-PMEAL Manager",
                "fr": "Combine planification stratégique et MEAL : conception des interventions et articulation du système MEAL avec la stratégie programme et les propositions aux bailleurs.",
                "en": "Combines strategic planning and MEAL: intervention design and articulation of the MEAL system with program strategy and donor proposals.",
            },
            {
                "code": "PMEAL-Spécialist",
                "fr": "Référent technique interne sur l'ensemble du champ MEAL : conception de systèmes, assurance qualité méthodologique, appui-conseil et renforcement des capacités des équipes.",
                "en": "Internal technical referent across the whole MEAL field: system design, methodological quality assurance, advisory support and team capacity building.",
            },
            {
                "code": "PMEAL-Database Administrator",
                "fr": "Conçoit, sécurise et gère les architectures de bases de données relationnelles complexes du programme ; gère les serveurs de données, les accès utilisateurs et les protocoles de sauvegarde.",
                "en": "Designs, secures, and manages complex relational database architectures for the program; manages data servers, user access, and backup protocols.",
            },
            {
                "code": "PMEAL-GIS Officer",
                "fr": "Spécialiste de la géomatique et de la cartographie humanitaire ; produit des cartes d'impact, analyse spatiale des données de couverture des projets et gère les géodatabases.",
                "en": "Specialist in geomatics and humanitarian mapping; produces impact maps, spatial analysis of project coverage data, and manages geodatabases.",
            },
            {
                "code": "PMEAL-Gender & Inclusion MEAL Advisor",
                "fr": "Veille à l'intégration systématique du genre, de l'équité, de l'inclusion du handicap et des approches sensibles au contexte dans tous les indicateurs et outils de collecte de données.",
                "en": "Ensures the systematic integration of gender, equity, disability inclusion, and context-sensitive approaches into all indicators and data collection tools.",
            },
            {
                "code": "PMEAL-Quality & Compliance Officer",
                "fr": "Vérifie le respect des standards humanitaires internationaux (Norme HAP, Core Humanitarian Standard) et des exigences de conformité des bailleurs de fonds au sein des projets.",
                "en": "Ensures compliance with international humanitarian standards (HAP, Core Humanitarian Standard) and donor compliance requirements across projects.",
            },
            {
                "code": "PMEAL-Research & Studies Officer",
                "fr": "Conçoit et pilote les études thématiques approfondies, les enquêtes de référence (baseline), à mi-parcours et finales, ainsi que les recherches opérationnelles.",
                "en": "Designs and manages in-depth thematic studies, baseline, mid-term, and final evaluations, as well as operational research.",
            },
            {
                "code": "PMEAL-Data Protection Officer",
                "fr": "Garantit la conformité des pratiques MEAL avec les réglementations sur la protection des données personnelles (RGPD, lois locales) et la sécurité de l'anonymat des bénéficiaires.",
                "en": "Ensures MEAL practices comply with personal data protection regulations (GDPR, local laws) and the security of beneficiary anonymity.",
            },
        ]

        count = 0
        for item in PROFILS:
            code = item["code"]
            intitule = code.replace("PMEAL-", "").replace("PMEAL_", "")

            profil, created = ProfilMeal.objects.update_or_create(
                code=code,
                defaults={
                    "intitule": intitule,
                    "description_fr": item["fr"],
                    "description_en": item["en"],
                },
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Créé : {code}"))
            else:
                self.stdout.write(f"Mis à jour : {code}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nChargement terminé avec succès ! ({count} nouveaux profils enregistrés)"
            )
        )