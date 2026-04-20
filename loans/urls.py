from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.loan_dashboard, name='loan_dashboard'),

    # Loan CRUD
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/create/', views.loan_create, name='loan_create'),
    path('loans/<int:pk>/', views.loan_detail, name='loan_detail'),
    path('loans/<int:pk>/approve/', views.loan_approve, name='loan_approve'),
    path('loans/<int:pk>/disburse/', views.loan_disburse, name='loan_disburse'),
    path('loans/<int:pk>/topup/', views.loan_topup, name='loan_topup'),
    path('loans/<int:pk>/schedule/', views.loan_emi_schedule, name='loan_emi_schedule'),

    # AJAX
    path('api/emi-calculate/', views.loan_emi_calculate, name='loan_emi_calculate'),
]
