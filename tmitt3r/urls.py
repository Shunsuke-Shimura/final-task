from django.urls import path

from . import views

app_name = 'tmitt3r'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('tm33t/', views.Tm33tView.as_view(), name='tm33t'),
]
