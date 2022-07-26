"""beone_web_app URL Configuration

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

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redirect_root),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html', next_page='/datasets'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login'), name='logout'),
    path('sample_list/', views.sample_list, name='sample_list'),
    path('datasets/', views.dataset_list, name='datasets'),
    path('datasets/<int:dataset_key>/', views.view_dataset, name='view_dataset'),
    path('datasets/<int:dataset_key>/edit/', views.edit_dataset, name='edit_dataset'),
    path('datasets/add_remove_sample/', views.add_remove_sample),
    path('dashboard/', views.sample_list, name='dashboard'),
    path('rt_jobs/', views.rt_jobs, name='rt_jobs'),
    path('rt_jobs/for_dataset/<int:dataset_key>/', views.rt_jobs, name='rt_jobs_for_dataset'),
    path('rt_jobs/<int:rt_job_key>/delete/', views.delete_rt_job, {'dataset_page': False}, name='delete_rt_job'),
    path('rt_jobs/<int:rt_job_key>/delete/for_dataset/', views.delete_rt_job, {'dataset_page': True}, name='delete_rt_job_for_dataset'),
    path('rt_jobs/<int:rt_job_key>/run/', views.run_rt_job, name='run_rt_job'),
    path('rt_jobs/<int:rt_job_key>/', views.view_rt_job, name='view_rt_job'),
    path('rt_jobs/<int:rt_job_key>/output/<str:item>/', views.view_rt_output, name='view_rt_output'),
    path('rt_jobs/<int:rt_job_key>/download/<str:item>/', views.download_rt_file, name='download_rt_file'),
    path('rt_jobs/<int:rt_job_key>/data/', views.get_rt_data),
    path('rt_jobs/<int:rt_job_key>/partitions/', views.get_partitions_for_job),
]
