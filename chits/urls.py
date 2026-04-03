from django.urls import path
from . import views

urlpatterns = [
    path('', views.chit_list, name='chit_list'),
    path('create/', views.chit_create, name='chit_create'),
    path('<int:pk>/edit/', views.chit_edit, name='chit_edit'),
    path('<int:pk>/', views.chit_detail, name='chit_detail'),
    path('<int:pk>/remove-member/<int:member_pk>/', views.remove_member, name='remove_member'),
]
