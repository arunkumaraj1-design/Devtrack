from django.urls import path
from . import views

urlpatterns = [
    path('reporters', views.reporters_view),
    path('reporters/', views.reporters_view),
    path('issues', views.issues_view),
    path('issues/', views.issues_view),
]
