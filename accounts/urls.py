from django.urls import path
from django.contrib.auth import views as auth_view

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_view.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_view.LogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', views.UserDetailView.as_view(), name='profile'),
    path('follow/', views.FollowView.as_view(), name='follow'),
    path('unfollow/', views.UnfollowView.as_view(), name='unfollow'),
    path('follows/', views.FollowsDetail.as_view(), name='follows')
]
