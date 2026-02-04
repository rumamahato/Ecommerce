from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.log_in, name='log_in'),
    path('logout/', views.log_out, name='log_out'),
    
    # Password Change (Logged in users)
    path("change_password/", views.change_password, name="change_password"),

    # Password Reset (Forgotten password)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    #profile_dashboard
    path("profile_dashboard/",views.profile_dashboard,name="profile_dashboard"),
    path("profile/",views.profile,name="profile"),
    path("my_order",views.my_order,name="my_order")


]
