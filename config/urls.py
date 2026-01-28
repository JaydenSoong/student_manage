"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.views.generic.base import RedirectView
from accounts.views import user_login, user_logout, change_password

urlpatterns = [
    path('', RedirectView.as_view(url='/students/', permanent=False)),
    path('admin/', admin.site.urls),
    path('grades/', include('grades.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('scores/', include('scores.urls')),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('change_password/', change_password, name='change_password')
]
