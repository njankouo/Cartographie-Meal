from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
     
    path('Inscription-meal-afrique/', views.MealAfrique, name='Inscription-meal-afrique'),
    
    path('count-members/', views.CountMembers, name='count-members'),
    
    path('check-email/', views.check_email_ajax, name='check-email'),
    
    path('synchronisation-data/', views.register_expert, name='synchronisation-data'),
    
    path('Information-members/<str:code>/', views.Information_members, name='Information-members'),
    
    path('cartographie-users/<str:code>/', views.Cartographie, name='cartographie-users'),
    
    path('Edit-Profil/<str:code>/', views.EditProfil, name='Edit-Profil'),
    
    path('Update-profil/', views.Updateprofil, name='Update-profil'),
    
    path('my-card-meal-afrique/', views.myCard, name='my-card-meal-afrique'),
    
    path('count-male-and-female/', views.count_male_and_female, name='count-members-male-and-female'),
    
    path('count-members-of-countries/', views.group_member_by_country, name='count-members-of-countries'),
    
    path('members-meal-afrique/<str:country>/', views.memberscountry, name='members-meal-afrique'),
    
    path('profil-expert/<str:code>', views.ProfilExpert, name='profil-expert'),
    
    path('api/get-cities/', views.get_cities_by_country, name='api_get_cities'),

    path('create-cartographie-meal/', views.secure_create_or_update_personnel, name='create-cartographie-meal'),

    path('authentification/', views.authentification, name='authentification')


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)