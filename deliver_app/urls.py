"""
URL configuration for deliver_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
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
from django.urls import path
from deliver_app import views 

urlpatterns = [
    path('delivery',views.Delivery.as_view(),name='delivery'),
    path('reports',views.Reports.as_view(),name='reports'),
    path('reports/all',views.AllReports.as_view(),name='all-reports'),
    path('reports/today',views.TodayReports.as_view(),name='today-reports'),
    path('reports/cumulative/daily',views.DailyCumulatives.as_view(),name='daily-cumulatives'),
    path('reports/cumulative/monthly',views.MonthlyCumulatives.as_view(),name='monthly-cumulatives'),
    path('reports/cumulative/email/daily',views.EmailDailyCumulative.as_view(),name='email-daily-cumulatives'),
    path('reports/cumulative/email/monthly',views.EmailMonthlyCumulative.as_view(),name='email-monthly-cumulatives'),
]
