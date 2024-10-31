from django.urls import path
from . import views

urlpatterns = [
    path('userRegistration/', views.UserRegistration, name='UserRegistration'),
    path('Analysis/<int:symptom_id>/', views.Analysis, name='Analysis'),
    path('symptoms/', views.symptoms, name='symptoms'),
    path('add-symptom/', views.add_symptom, name='add_symptom'),
    path('CheckUp/', views.CheckUp, name='CheckUp'),
    path('test_view/', views.test_view, name='test_view'),
    path('checkup/submit/', views.submit_checkup, name='submit_checkup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('analyze-symptoms/<int:symptom_id>/', views.analyze_symptoms, name='analyze_symptoms'),
    path('about_us/', views.about_us, name='about_us'),

]


