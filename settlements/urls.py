from django.urls import path
from . import views

urlpatterns = [
    path('', views.settlement_list, name='settlement_list'),
    path('create/', views.settlement_create, name='settlement_create'),
    path('<int:pk>/edit/', views.settlement_edit, name='settlement_edit'),
    path('<int:pk>/', views.settlement_detail, name='settlement_detail'),
]
