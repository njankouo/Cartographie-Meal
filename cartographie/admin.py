from django.contrib import admin
from .models import (
    ProfilMeal,
    Personnel,
    ProfilPersonnel,
    DomaineExpertise,
    PersonnelDomaine,
    SecteurIntervention,
    PersonnelSecteurIntervention,
    OutilsMeal,
    PersonnelOutilMeal,
    DisponibilityType,
    PersonnelDisponibilityType,
    Baniere,
    Rubrique,
    Sous_Rubrique,
    Actualite,
    SousActualite,
)

# Enregistrement des modèles simples
admin.site.register(ProfilMeal)
admin.site.register(DomaineExpertise)
admin.site.register(SecteurIntervention)
admin.site.register(OutilsMeal)
admin.site.register(DisponibilityType)
admin.site.register(Baniere)
admin.site.register(Rubrique)
admin.site.register(Sous_Rubrique)
admin.site.register(ProfilPersonnel)
admin.site.register(PersonnelDomaine)
admin.site.register(PersonnelSecteurIntervention)
admin.site.register(PersonnelOutilMeal)
admin.site.register(PersonnelDisponibilityType)


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "nom",
        "prenom",
        "mail",
        "tel",
        "fonction",
        "country",
        "is_active",
        "current_profil",
    )
    list_filter = (
        "is_active",
        "country",
        "current_profil",
        "organization_type",
        "level_expertise",
    )
    search_fields = (
        "code",
        "nom",
        "prenom",
        "mail",
        "fonction",
        "parcours_meal",
    )
    filter_horizontal = ("collaborateurs",)


@admin.register(Actualite)
class ActualiteAdmin(admin.ModelAdmin):
    list_display = ("intitule", "rubrique", "sous_rubrique", "date", "is_public")
    list_filter = ("is_public", "rubrique", "sous_rubrique", "date")
    search_fields = ("intitule", "description")
    prepopulated_fields = {"slug": ("intitule",)}


@admin.register(SousActualite)
class SousActualiteAdmin(admin.ModelAdmin):
    list_display = (
        "intitule",
        "actualite",
        "baniere",
        "date",
    )
    list_filter = ("date", "actualite")
    search_fields = ("intitule", "description")
    prepopulated_fields = {"slug": ("intitule",)}