from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.log_list, name='log_list'),
    path('export/', views.export_dashboard, name='export_dashboard'),
    path('export/members/', views.export_members, name='export_members'),
    path('export/payments/', views.export_payments, name='export_payments'),
    path('settings/', views.settings_view, name='system_settings_view'),
]
