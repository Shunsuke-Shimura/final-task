from django.urls import path

from . import views

app_name = 'tmitt3r'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('tm33t/', views.Tm33tView.as_view(), name='tm33t'),
    path('tm33t/detail/<int:pk>', views.Tm33tDetailView.as_view(), name='detail'),
    path('tm33t/reply/<int:pk>', views.Tm33tReplyView.as_view(), name='reply'),
    path('tm33t/like/', views.Tm33tLikeView.as_view(), name='like'),
]
