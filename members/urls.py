from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('create/', views.member_create, name='member_create'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('<int:pk>/upload-document/', views.member_document_upload, name='member_document_upload'),
    path('kyc-center/', views.kyc_center, name='kyc_center'),
]
