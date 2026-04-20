from django.urls import path
from . import views

urlpatterns = [
    # Customers
    path('', views.loan_customer_list, name='loan_customer_list'),
    path('create/', views.loan_customer_create, name='loan_customer_create'),
    path('<int:pk>/', views.loan_customer_detail, name='loan_customer_detail'),
    path('<int:pk>/edit/', views.loan_customer_edit, name='loan_customer_edit'),
    path('<int:pk>/delete/', views.loan_customer_delete, name='loan_customer_delete'),

    # Agents
    path('agents/', views.loan_agent_list, name='loan_agent_list'),
    path('agents/create/', views.loan_agent_create, name='loan_agent_create'),
    path('agents/<int:pk>/edit/', views.loan_agent_edit, name='loan_agent_edit'),
    path('agents/<int:pk>/customers/', views.loan_agent_api_customers, name='loan_agent_api_customers'),
    path('agents/my-dashboard/', views.loan_agent_dashboard, name='loan_agent_dashboard'),

    # Portal
    path('portal/', views.loan_customer_portal, name='loan_customer_portal'),
    path('portal/loans/', views.loan_customer_my_loans, name='loan_customer_my_loans'),
    path('portal/loans/<int:loan_pk>/emi/', views.loan_customer_my_emi, name='loan_customer_my_emi'),
    path('portal/payments/', views.loan_customer_my_payments, name='loan_customer_my_payments'),
]
