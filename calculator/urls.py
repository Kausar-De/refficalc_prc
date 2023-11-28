from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.registerPage, name = "register"),
    path('login/', views.loginPage, name = "login"),
    path('logout/', views.logoutUser, name = "logout"),
    path('user/', views.buildingPage, name = "user"),
    path('account/', views.accountSettings, name = "account"),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name = "calculator/password_reset.html"), name = "reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name = "calculator/password_reset_sent.html"), name = "password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = "calculator/password_reset_form.html"), name = "password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name = "calculator/password_reset_done.html"), name = "password_reset_complete"),

    path('', views.home, name = "home"),
    path('calculate/', views.calculate, name = "calculate"),
    path('result/', views.result, name = "result"),
    path('database/', views.database, name = "database"),
    path('flats/', views.flats, name = "flats"),

    path('updateflat/<str:pk>', views.updateFlat, name = "updateflat"),
    path('updateappliance/<str:pk>', views.updateAppliance, name = "updateappliance"),
    path('benchmark/<str:pk>', views.benchmark, name = "benchmark"),
    path('removeflat/<str:pk>', views.removeFlat, name = "removeflat"),
    path('building/<str:pk>', views.building, name = "building"),
    path('smartmeter/', views.iotReading, name = "smartmeter"),
]