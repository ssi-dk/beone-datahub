"""comparison_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views

from comparisons import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redirect_root),
    path('login/', auth_views.LoginView.as_view(template_name='comparisons/login.html', next_page='/comparisons'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login'), name='logout'),
    path('samples/', views.sample_list, name='sample_list'),
    path('comparisons/', views.comparison_list, name='comparison_list'),
    path('comparisons/<int:comparison_id>/make_tree/<str:tree_type>', views.make_tree, name='make_tree'),
    path('launchpad/<str:tree_id>/', views.launchpad, name='launchpad'),
]
