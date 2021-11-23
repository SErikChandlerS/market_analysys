from django.urls import path
from . import views

urlpatterns = [
    path('', views.load_statistics.as_view(), name='main_page'),
    path('load_vacancies', views.load_vacancies.as_view(), name='load_vacancies'),
    path('load_cvs', views.load_cvs.as_view(), name='load_cvs'),
    path('load_statistics', views.load_statistics.as_view(), name='main_page'),
    path('table', views.load_cvs.as_view(), name='table'),
]
