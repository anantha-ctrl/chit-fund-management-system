from django.urls import path
from . import views

urlpatterns = [
    # Pay an EMI
    path('pay/<int:loan_pk>/', views.record_payment, name='record_payment'),

    # Receipt
    path('receipt/<int:pk>/', views.payment_receipt, name='loan_payment_receipt'),

    # History & Reporting
    path('history/', views.payment_history, name='loan_payment_history'),
    path('overdue/', views.overdue_emis, name='loan_overdue_emis'),
    path('daily/', views.daily_collection, name='loan_daily_collection'),

    # Transaction Ledger
    path('ledger/', views.transaction_ledger, name='loan_transaction_ledger'),
    path('ledger/<int:loan_pk>/', views.transaction_ledger, name='loan_transaction_ledger_detail'),

    # Customer Portal Actions
    path('submit-proof/<int:emi_pk>/', views.customer_loan_submit_proof, name='customer_loan_submit_proof'),

    # Staff Proof Management
    path('proofs/', views.admin_loan_proof_list, name='admin_loan_proof_list'),
    path('proofs/<int:proof_pk>/<str:action>/', views.process_loan_proof, name='process_loan_proof'),
    # Export
    path('export/csv/', views.export_loan_payments, name='export_loan_payments'),
]
