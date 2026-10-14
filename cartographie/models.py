from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.
class ProfilMeal(models.Model):
    intitule = models.CharField(max_length=255)
    description = models.TextField()

class Personnel(models.Model):
    nom	= models.CharField(max_length=128,blank=True,null=True)
    prenom = models.CharField(max_length=128,blank=True,null=True)
    mail = models.CharField(max_length=128,blank=True,null=True)
    tel = models.CharField(max_length=128,blank=True,null=True)
    photo = models.FileField(blank=True,null=True)
    sexe= models.CharField(max_length=255,null=True,blank=True)
    bd_user = models.OneToOneField(User,blank=True,null=True,on_delete = models.SET_NULL)
    
    fonction = models.CharField(max_length = 255, null=True)

    country = models.CharField(max_length=128,blank=True,null=True)

    is_active = models.BooleanField(default=False)
    
    collaborateurs = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='parent')

    nationalite = models.CharField(max_length=255, null=True)

    code = models.CharField(max_length=255, null=True)

    parcours_meal = models.TextField(null=True)

    date_enregistrement = models.DateField(null=True)

    current_profil = models.ForeignKey(ProfilMeal, on_delete=models.CASCADE, null=True)

    years_expertise = models.IntegerField(null=True)

    level_expertise = models.CharField(max_length=255, null=True)

    is_speeck_french = models.BooleanField(default=False)

    is_speeck_english = models.BooleanField(default=False)

    other_language = models.TextField(max_length=255)

    describe_certification = models.TextField(null=True)

    def __str__(self):
        return self.code or f"{self.nom} {self.prenom}"
    

class ProfilPersonnel(models.Model):
    profil = models.ForeignKey(ProfilMeal, on_delete=models.CASCADE, null=True)
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=True)
    year_experience= models.IntegerField(null=True)


class DomaineExpertise(models.Model):
    intitule = models.CharField(max_length=255)
    description= models.TextField()

class PersonnelDomaine(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=True)
    domaine = models.ForeignKey(DomaineExpertise, on_delete=models.CASCADE, null=True)

class SecteurIntervention(models.Model):
    intitule = models.CharField(max_length=255)
    description= models.TextField()

class PersonnelSecteurIntervention(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=True)
    secteur_intervention = models.ForeignKey(SecteurIntervention, on_delete=models.CASCADE, null=True)


class OutilsMeal(models.Model):

    intitule = models.CharField(max_length=255)
    description= models.TextField()

class PersonnelOutilMeal(models.Model):
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=True)
    outil_meal = models.ForeignKey(OutilsMeal, on_delete=models.CASCADE, null=True)

class DisponibilityType(models.Model):
    intitule = models.CharField(max_length=255)
    description= models.TextField()

class PersonnelDisponibilityType(models.Model):

    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, null=True)
    type_disponibilite = models.ForeignKey(DisponibilityType, on_delete=models.CASCADE, null=True)
class Baniere(models.Model):
    nom = models.CharField(max_length=255,null=True,blank=True)

    logo = models.FileField(null=True,blank=True)

class Rubrique(models.Model):
    nom = models.CharField(max_length=255,null=True,blank=True)

class Sous_Rubrique(models.Model):
    nom = models.CharField(max_length=255,null=True,blank=True)
    rubrique = models.ForeignKey(Rubrique,on_delete = models.SET_NULL,null=True,blank=True)



class Actualite(models.Model):
    slug = models.SlugField(max_length=255, null=True, blank=True)
    intitule = models.CharField(null=True,blank=True,max_length=255)
    description = models.TextField(null=True,blank=True)
    photos = models.FileField(null=True,blank=True)
    documents = models.FileField(null=True,blank=True)
    rubrique = models.ForeignKey(Rubrique,on_delete = models.SET_NULL,null=True,blank=True)
    sous_rubrique = models.ForeignKey(Sous_Rubrique,on_delete = models.SET_NULL,null=True,blank=True)
    date = models.DateField(null=True,blank=True)
    is_public = models.BooleanField(null=True)

    
    
    def save(self, *args, **kwargs):
        # Génère automatiquement le slug à partir du titre s'il n'existe pas
        if not self.slug:
            self.slug = slugify(self.intitule)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
      
        return reverse('acticle-detail', kwargs={'slug': self.slug})

class SousActualite(models.Model):
    slug = models.SlugField(max_length=255, null=True, blank=True)
    intitule=models.CharField(null=True,max_length=255)
    description= models.TextField(null=True)
    photos = models.ImageField(upload_to="generate_filename", blank=True, null=True)
    documents = models.FileField(upload_to="generate_filename", blank=True, null=True)
    actualite=models.ForeignKey(Actualite,null=True,on_delete = models.SET_NULL)
    baniere= models.ForeignKey(Baniere,on_delete = models.SET_NULL,null=True)
  
    date = models.DateField(null=True,blank=True)
    
    
    def save(self, *args, **kwargs):
        # Génère automatiquement le slug à partir du titre s'il n'existe pas
        if not self.slug:
            self.slug = slugify(self.intitule)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
      
        return reverse('article-connexe', kwargs={'slug': self.slug})


