from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/toggle/', views.toggle_notification_read, name='toggle_notification_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete_notification'),
    path('<int:pk>/read/', views.mark_individual_read, name='mark_notification_read'),
    path('clear-all/', views.delete_all_notifications, name='clear_all_notifications'),
    path('bulk/', views.bulk_notification_view, name='bulk_notification'),
]
