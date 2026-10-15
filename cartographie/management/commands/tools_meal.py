from django.core.management.base import BaseCommand
from cartographie.models import OutilsMeal

class Command(BaseCommand):
    help = "Charge ou met à jour les outils MEAL dans la base de données"

    def handle(self, *args, **kwargs):
        OUTILS = [
            {
                'id': 'kobo',
                'intitule': 'KoboToolbox',
                'fr': "Plateforme de collecte de données mobiles (CAPI) gratuite et open-source largement utilisée dans le secteur humanitaire pour les enquêtes hors-ligne et le suivi terrain.",
                'en': "Free and open-source mobile data collection platform (CAPI) widely used in the humanitarian sector for offline surveys and field monitoring."
            },
            {
                'id': 'odk',
                'intitule': 'ODK',
                'fr': "Open Data Kit (ODK) est une suite d'outils open-source pour la collecte, la gestion et l'utilisation de données dans les environnements à ressources limitées.",
                'en': "Open Data Kit (ODK) is an open-source suite of tools for collecting, managing, and using data in resource-constrained environments."
            },
            {
                'id': 'commcare',
                'intitule': 'CommCare',
                'fr': "Plateforme mobile conçue pour le suivi de cohortes, le soutien aux agents de santé/terrain et la gestion complexe de dossiers de bénéficiaires.",
                'en': "Mobile platform designed for case management, field worker decision support, and tracking longitudinal beneficiary data."
            },
            {
                'id': 'dhis2',
                'intitule': 'DHIS2',
                'fr': "Système d'information de gestion de la santé (HMIS) open-source utilisé à l'échelle nationale et organisationnelle pour le suivi des indicateurs agrégés et individuels.",
                'en': "Open-source Health Management Information System (HMIS) used nationally and globally for tracking aggregate and individual health data and MEAL indicators."
            },
            {
                'id': 'powerbi',
                'intitule': 'Power BI',
                'fr': "Solution d'analyse décisionnelle et de Business Intelligence de Microsoft permettant de modéliser des données et de créer des tableaux de bord interactifs.",
                'en': "Microsoft Business Intelligence platform used for data modeling, visualization, and building interactive program dashboards."
            },
            {
                'id': 'activityinfo',
                'intitule': 'ActivityInfo',
                'fr': "Logiciel de gestion de données et de suivi-évaluation conçu pour la coordination humanitaire, la cartographie des activités (3W/5W) et la gestion d'indicateurs.",
                'en': "Information management software built for humanitarian coordination, activity mapping (3W/5W), and monitoring and evaluation tracking."
            },
            {
                'id': 'surveycto',
                'intitule': 'SurveyCTO',
                'fr': "Plateforme sécurisée de collecte de données basée sur ODK, optimisée pour la recherche rigoureuse, les évaluations d'impact et le contrôle qualité en temps réel.",
                'en': "Secure ODK-based mobile data collection platform optimized for rigorous research, impact evaluations, and real-time data quality control."
            },
            {
                'id': 'ms365',
                'intitule': 'MS 365 / Power Automate',
                'fr': "Suite bureautique et outil d'automatisation des flux de travail (SharePoint, Forms, Power Automate, Excel) pour la gestion et la circulation de l'information MEAL.",
                'en': "Productivity suite and workflow automation engine (SharePoint, Forms, Power Automate, Excel) for managing and streamlining MEAL information flows."
            },
            {
                'id': 'opti',
                'intitule': 'OPTI',
                'fr': "Système intégré de gestion de programmes et de suivi-évaluation pour la planification, le suivi budgétaire et la performance des projets.",
                'en': "Integrated program management and M&E software used for operational planning, indicator performance, and project tracking."
            },
            {
                'id': 'operaplus',
                'intitule': 'OPERAPLUS',
                'fr': "Progiciel de gestion et de suivi opérationnel des projets et programmes de développement.",
                'en': "Operational management and monitoring software package for development projects and programs."
            }
        ]

        count = 0
        for item in OUTILS:
            code = item['id']
            intitule = item['intitule']

            outil, created = OutilsMeal.objects.update_or_create(
                code=code,
                defaults={
                    'intitule': intitule,
                    'description_fr': item['fr'],
                    'description_en': item['en'],
                }
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Créé : {intitule} ({code})"))
            else:
                self.stdout.write(f"Mis à jour : {intitule} ({code})")

        self.stdout.write(self.style.SUCCESS(f"\nChargement des outils MEAL terminé ! ({count} nouveaux créés)"))