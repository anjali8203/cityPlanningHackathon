"""

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import CustomSignUpView, login_view

urlpatterns = [
    path("", views.landing_page, name="homepage"),
    path("admin/", admin.site.urls),
    path("accounts/signup/", CustomSignUpView.as_view(), name="account_signup"),
    path("accounts/login/", views.CustomLoginView.as_view(), name="account_login"),
    path('accounts/logout/', views.logout_view, name='account_logout'),
    path("accounts/", include("allauth.urls")),
    path('login/', login_view, name='login'),
    path("create_profile/", views.create_user_profile, name="create_user_profile"),
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),
    path("login_redirect/", views.login_redirect, name="login_redirect"),
    path('your_projects/', views.your_projects, name='your_projects'),
    path("view_profile/", views.view_profile, name="view_profile"),
    # path('travel-guide/', views.travel_guide, name='travel_guide'),
    # path('project/vote/', views.vote, name='vote'),
    path('city/<str:city_name>/', views.city_landmarks, name='city_landmarks'),
# Add project management URLs
    path('projects/owned/', views.your_projects, name='your_projects'),
    path('update_points/', views.update_points, name='update_points'),
    path("projects/create/", views.create_project, name="create_project"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),

    path("projects/<int:project_id>/post_message/", views.post_project_message, name="post_message"),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),



]