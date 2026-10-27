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
    
    path('Information-members/', views.Information_members, name='Information-members'),
    
    path('cartographie-users/', views.Cartographie, name='cartographie-users'),
    
    path('Edition-Profil/', views.EditProfil, name='Edition-Profil'),
    
    path('Update-profil/', views.Updateprofil, name='Update-profil'),
    
    path('my-card-meal-afrique/', views.myCard, name='my-card-meal-afrique'),
    
    path('count-male-and-female/', views.count_male_and_female, name='count-members-male-and-female'),
    
    path('count-members-of-countries/', views.group_member_by_country, name='count-members-of-countries'),
    
    path('members-meal-afrique/<str:country>/', views.memberscountry, name='members-meal-afrique'),
    
    path('profil-expert/', views.ProfilExpert, name='profil-expert'),
    
    path('api/get-cities/', views.get_cities_by_country, name='api_get_cities'),

    path('create-cartographie-meal/', views.secure_create_or_update_personnel, name='create-cartographie-meal'),

    path('authentification/', views.authentification, name='authentification'),

    path('admin-auth/send-code/', views.VerificationEmailUser, name='admin-auth-send-code'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('admin-auth/verify-code/', views.ValiderCodeView, name='admin-auth-verify-code'),

    path('verification-otp/', views.VerificationCodeUser, name='verification-otp'),

    path('verification_otp_view/', views.verification_otp_view, name='verification_otp_view'),

    path('deconnexion-view/', views.deconnexion_view, name='deconnexion-view'),

    path('check_email_page/', views.check_email_page, name='check_email_page'),

    path('send-mail/', views.send_mail, name='send-mail'),

    path('actualite/', views.actualite, name='actualite'),

    path('logout_admin/', views.logout_admin, name='logout_admin'),

    path('zone-intervention/', views.zone_intervention, name='zone-intervention'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns