from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('create/', views.payment_create, name='payment_create'),
    path('<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('<int:pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('bulk-reminders/', views.bulk_reminder_view, name='bulk_reminders'),
]
