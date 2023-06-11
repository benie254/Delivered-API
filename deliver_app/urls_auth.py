from django.urls import path, re_path as url, include 
from deliver_app import views_auth
from knox import views as knox_views

# url patterns/configs 
urlpatterns = [
    path('password/change/<int:pk>',views_auth.ChangePassword.as_view(),name='change-password'),
    url(r'^password/reset/request$',views_auth.PasswordResetRequest.as_view(),name='reset-password-request'),
    path('password/reset/confirmed/<int:pk>',views_auth.ResetPassword.as_view(),name='reset-password-confirmed'),
    path('password/reset/complete/<slug:uidb64>/<slug:token>',views_auth.activate,name='reset-password-complete'),
    url(r'^auth/',include('knox.urls')),
    url(r'^auth/register$',views_auth.Register.as_view(),name='register'),
    url(r'^auth/login$',views_auth.Login.as_view(),name='login'),
    url(r'^auth/logout$',knox_views.LogoutView.as_view(),name='logout'),
    url(r'^profile$',views_auth.UserView.as_view(),name='user'),
    path('update/<int:pk>',views_auth.UpdateUser.as_view(),name='update-user'),
    url(r'^profiles/all$',views_auth.UserProfiles.as_view(),name='all-users'),
    url(r'^admins/all$',views_auth.AllAdmins.as_view(),name='all-admins'),
]