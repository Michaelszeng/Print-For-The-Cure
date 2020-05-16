from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.home, name='home'),

    path('catalogue-shield/', views.catalogueShield, name='catalogue item face shield'),
    path('catalogue-maskstrap/', views.catalogueMaskStrap, name='catalogue item mask strap'),
    path('catalogue-handle/', views.catalogueHandle, name='catalogue item door handle'),
    path('catalogue-dooropener/', views.catalogueDoorOpener, name='catalogue item door opener'),

    path('donorGuide/', views.donorGuidePDF, name='donor guide'),
    path('register/', views.donorRegistration, name='donor registration'),
    path('registrationSuccessful/', views.registrationSuccessful, name='registration sucessful'),
    path('login/', views.donorLogin, name='login'),
    path('requestPPE/', views.doctorRequest, name='doctors submit requests'),
    path('requestSubmitSuccessful/', views.requestSubmitSuccessful, name="request submitted successfully"),
    path('requestsVisual/', views.map, name="visual map of requests"),
    path('nearbyRequests/', views.nearbyRequests, name='nearby requests'),
    path('notLoggedIn/', views.notLoggedIn, name='not logged in'),
    path('confirmation/', views.confirmClaim, name='confirmation'),
    path('confirmation1/', views.confirmClaim1, name='confirmation returns to mapview'),
    path('thankyou/', views.thankYou, name='thank you page'),
    path('register/terms', views.terms, name='terms page'),
    path('pp', views.pp, name='privacy policy'),
    path('requestPPE/terms', views.terms, name='terms page'),

    path('requestDetails/', views.requestDetails, name='details page for request from nearbyRequests.html'),
    path('statusCheck/', views.status, name='status check'),

    #url(r'^django_popup_view_field/', include('django_popup_view_field.urls', namespace="django_popup_view_field")),

    path('test/', views.test)
]
