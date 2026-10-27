# MEAL Afrique — journal et espace d'administration

Site Django du journal **MEAL Afrique** (suivi, évaluation, redevabilité et apprentissage en Afrique), relié à la plateforme **OPERAPLUS / BeINfos+**. Il publie des débats, des dépêches, un agenda d'événements et un fil d'actualité défilant, en français et en anglais. L'équipe éditoriale gère ces contenus depuis un espace d'administration dédié.

> Les éléments entre `<…>` sont à compléter avec les valeurs réelles de votre projet.

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Technologies](#technologies)
3. [Structure du projet](#structure-du-projet)
4. [Installation en local](#installation-en-local)
5. [Configuration](#configuration)
6. [Espace d'administration](#espace-dadministration)
7. [Modèle Actualite](#modèle-actualite)
8. [Conventions de développement](#conventions-de-développement)
9. [Déploiement](#déploiement)
10. [Dépannage](#dépannage)
11. [Lien avec OPERAPLUS](#lien-avec-operaplus)

---

## Fonctionnalités

### Journal public
- **À la une** : un seul contenu mis en avant à la fois, en général le débat en cours.
- **Dernières dépêches** : liste des actualités récentes.
- **Agenda** : événements avec date, horaires, lieu et lien d'inscription.
- **Fil « En direct »** : bandeau défilant en haut de page.
- **Bilingue** : chaque contenu a une version française obligatoire et une version anglaise facultative.
- **Carte des pays** : chaque actualité peut être reliée à un ou plusieurs pays africains (codes ISO), partagés avec la carte MEAL Afrique / OPERAPLUS.

### Espace d'administration (personnel autorisé)
- **Actualités et débats** : création, modification, publication, mise à la une, suppression, avec aperçu en direct et contrôle qualité avant publication.
- **Brouillon automatique** : la saisie est sauvegardée sur l'appareil et peut être reprise après une fermeture accidentelle. Le raccourci `Ctrl + S` enregistre.
- **Communication** : envoi de mails groupés aux membres et historique des envois.
- **Données** : statuts et journal des synchronisations des sources de données, avec alerte en cas d'échec.

---

## Technologies

| Élément | Choix |
|---|---|
| Langage | Python `<3.12>` |
| Framework | Django `<5.x>` |
| Base de données | `<PostgreSQL / SQLite en local>` |
| Gabarits | Gabarits Django, HTML et CSS écrits à la main, JavaScript sans framework |
| Polices | Fraunces (titres), Plus Jakarta Sans (texte), JetBrains Mono (étiquettes), via Google Fonts |
| Fichiers envoyés | Images et documents joints dans `MEDIA_ROOT` (`actualites/` et `actualites/pj/`) |

---

## Structure du projet

```text
<meal_afrique>/                # dossier racine du projet
├── manage.py
├── requirements.txt
├── .env.example               # modèle des variables d'environnement
├── <config>/                  # réglages Django : settings.py, urls.py, wsgi.py
├── <actualites>/              # application des actualités et débats
│   ├── models.py              # modèle Actualite
│   ├── views.py               # vue admin_actualites (formulaire classique)
│   ├── urls.py
│   └── templates/
│       └── actualites.html    # page d'administration des actualités
├── templates/                 # gabarits partagés (journal public, mail groupé, synchronisations)
├── static/                    # CSS, JavaScript, images
└── media/                     # fichiers envoyés (non versionné)
```

Adaptez les noms entre `<…>` à votre arborescence réelle.

---

## Installation en local

```bash
# 1. Récupérer le code
git clone <url-du-depot> meal-afrique
cd meal-afrique

# 2. Environnement virtuel
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Variables d'environnement
cp .env.example .env               # puis remplir les valeurs

# 5. Base de données et compte administrateur
python manage.py migrate
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

- Journal : http://127.0.0.1:8000/
- Espace admin des actualités : http://127.0.0.1:8000/`<chemin-de-admin-actualites>`
- Admin Django : http://127.0.0.1:8000/admin/

---

## Configuration

Variables attendues dans `.env` (à adapter à votre `settings.py`) :

| Variable | Rôle | Exemple |
|---|---|---|
| `SECRET_KEY` | Clé secrète Django | chaîne longue et aléatoire |
| `DEBUG` | Mode débogage (jamais `True` en production) | `False` |
| `ALLOWED_HOSTS` | Domaines autorisés | `mealafrique.org,www.mealafrique.org` |
| `DATABASE_URL` | Connexion à la base | `postgresql://utilisateur:motdepasse@hote:5432/meal_afrique` |
| `TIME_ZONE` | Fuseau horaire | `Africa/Douala` |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Serveur d'envoi des mails groupés | `<fournisseur SMTP>` |
| `MEDIA_ROOT`, `MEDIA_URL` | Stockage des images et documents | `/var/www/meal-afrique/media`, `/media/` |

Ne versionnez jamais le fichier `.env`. Ajoutez-le au `.gitignore`, avec `media/`.

Réglages Django utiles :

```python
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Douala"
USE_TZ = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024   # documents joints jusqu'à 10 Mo
```

---

## Espace d'administration

### Noms d'URL utilisés par les gabarits

| Nom d'URL | Page |
|---|---|
| `admin-actualites` | Liste et formulaire des actualités (`?modifier=<id>` pour modifier) |
| `admin-actualite-basculer` | Bascule « publié » ou « à la une » (POST, champ `champ`) |
| `admin-actualite-supprimer` | Suppression d'une actualité (POST) |
| `admin-mail-groupe` | Envoi de mail groupé et historique (`#envois`) |
| `admin-synchronisations` | Statuts et journal des synchronisations (`#journal`) |
| `admin:index`, `admin:logout` | Admin Django et déconnexion |

Toutes ces vues sont réservées au personnel (`@staff_member_required`).

### Types de contenu

| Type | Valeur | Où il apparaît | Champs propres |
|---|---|---|---|
| Débat structuré | `debat` | Grand bloc « À la une » | `numero` (obligatoire), `statut` : `a_venir`, `en_cours`, `cloture` |
| Dépêche | `depeche` | Liste « Dernières dépêches » | — |
| Événement | `agenda` | Encadré « Agenda » | `date_evenement` (obligatoire), `date_fin_evenement`, `heure_debut`, `heure_fin`, `lieu`, `lien_inscription` |
| Fil d'actualité | `fil` | Bandeau défilant uniquement | — |

### Règles de publication
- Un contenu **à la une** est forcément publié, et il remplace celui qui l'était déjà.
- Un contenu non publié reste en **brouillon**, visible seulement dans l'espace admin.
- Une **date de retrait** retire automatiquement le contenu du journal.
- L'**étiquette** du fil (ex. `DÉBAT N°13`) et le **slug** sont générés s'ils sont laissés vides.

---

## Modèle Actualite

| Groupe | Champs |
|---|---|
| Type et débat | `type`, `numero`, `statut` |
| Événement | `date_evenement`, `date_fin_evenement`, `heure_debut`, `heure_fin`, `lieu`, `lien_inscription` |
| Contenu français | `titre_fr` (obligatoire), `resume_fr`, `contenu_fr` |
| Contenu anglais | `titre_en`, `resume_en`, `contenu_en` |
| Liens et médias | `lien`, `image`, `legende_image`, `credit_image`, `lien_video`, `piece_jointe`, `piece_jointe_titre` |
| Classement | `rubrique`, `source_nom`, `pays` (codes ISO séparés par des virgules, ex. `CM,SN,CI`), `tags` (12 au maximum) |
| Diffusion | `publie`, `a_la_une`, `dans_le_fil`, `etiquette`, `date_publication`, `date_expiration` |
| Référencement | `slug`, `meta_description` (160 caractères) |
| Suivi | `auteur` |

Après toute modification du modèle :

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Conventions de développement

Ces règles protègent le design et le JavaScript existants.

1. **Formulaires HTML classiques.** Les champs sont écrits à la main dans les gabarits (`<input>`, `<select>`, `<textarea>`). On n'utilise pas `{{ form }}` ni `{{ form.champ }}` pour l'affichage. La vue lit directement `request.POST` et `request.FILES`, puis renvoie les erreurs dans un dictionnaire `erreurs` (clé = nom du champ, `general` pour une erreur globale).
2. **Ne jamais renommer l'existant.** Les `id`, `name`, classes CSS, variables de gabarit et fonctions JavaScript existants restent tels quels : on **ajoute** du code, on ne modifie pas l'ancien. Les scripts de la page s'appuient sur ces noms, par exemple `id_titre_fr`, `id_publie`, `#formulaire`, `#pvCard`.
3. **Convention des `id`** : chaque champ porte `name="<champ>"` et `id="id_<champ>"`.
4. **Ajouts CSS et JavaScript** dans un nouveau bloc `<style>` ou `<script>` commenté (`/* Ajout : … */`), placé après les blocs existants.
5. **Accessibilité** : chaque champ a son `<label for="…">`, les erreurs sont affichées en texte, la navigation au clavier reste possible.
6. **Langue** : interface en français ; contenus en français et en anglais.

---

## Déploiement

Liste de contrôle avant la mise en ligne :

- [ ] `DEBUG=False` et `ALLOWED_HOSTS` renseigné
- [ ] `SECRET_KEY` propre à la production, hors du dépôt
- [ ] `python manage.py migrate`
- [ ] `python manage.py collectstatic --noinput`
- [ ] Dossier `media/` servi par le serveur web et sauvegardé
- [ ] HTTPS actif, `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
- [ ] Sauvegarde automatique de la base de données
- [ ] `python manage.py check --deploy` sans avertissement bloquant

Hébergement : `<serveur, Gunicorn + Nginx, ou plateforme utilisée>`.

---

## Dépannage

| Problème | Cause probable | Solution |
|---|---|---|
| Un champ saisi n'est pas enregistré | Le champ n'existe pas dans le modèle ou n'est pas lu dans la vue | Ajouter le champ au modèle (migration) et à la lecture de `request.POST` |
| L'image ou le document n'est pas enregistré | Formulaire sans `enctype="multipart/form-data"` ou vue qui ignore `request.FILES` | Vérifier les deux |
| Erreur « CSRF verification failed » | `{% csrf_token %}` absent du formulaire | L'ajouter dans chaque `<form method="post">` |
| Les dates s'affichent décalées d'une heure | Fuseau horaire | `TIME_ZONE = "Africa/Douala"` et `USE_TZ = True` |
| Les polices ne s'affichent pas | Accès à Google Fonts bloqué | Héberger les polices dans `static/` |
| Deux contenus à la une | Mise à la une hors de la vue prévue | Passer par la vue, qui retire la une précédente |

---

## Lien avec OPERAPLUS

MEAL Afrique et OPERAPLUS sont liés en permanence :

- **Pays** : les codes pays des actualités (`pays`) sont les mêmes que ceux de la carte OPERAPLUS, pour relier chaque contenu aux données du pays.
- **Synchronisations** : la page « Données » de l'espace admin suit l'état des échanges de données entre les deux plateformes.
- **Signature** : le pied de page de l'espace admin indique « MEAL Afrique · OPERAPLUS / BeINfos+ ».

Décrivez ici les points d'échange précis entre les deux projets (API, exports, fréquence des synchronisations) : `<à compléter>`.

---

## Équipe et contact

- Responsable du projet : `<nom>`
- Contact : `<adresse e-mail>`
- Licence : `<licence ou « Tous droits réservés »>`
