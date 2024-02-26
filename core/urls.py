from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('communication-plan/', views.communication_plan, name='communication_plan'),
    path('goals/', views.goals, name='goals'),
    path('strategies-objectives/', views.strategies_objectives, name='strategies_objectives'),
    path('community-activities/', views.community_activities, name='community_activities'),
    path('partner-activities/', views.partner_activities, name='partner_activities'),
    path('create-community-activity/', views.community_activities, name='create_community_activity'),
    path('create-partner-activity/', views.partner_activities, name='create_partner_activity'),
    path('community-collaboratives/', views.community_collaboratives, name='community_collaboratives'),
    path('activities', views.activities, name='activities')
]
