from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.loan_summary_report, name='loan_summary_report'),
    path('pending-emis/', views.pending_emi_report, name='loan_pending_emi_report'),
    path('overdue/', views.overdue_report, name='loan_overdue_report'),
    path('branch-performance/', views.branch_performance_report, name='loan_branch_performance'),
    path('monthly-collection/', views.monthly_collection_report, name='loan_monthly_collection'),
    path('periodic-collection/', views.loan_collection_report, name='loan_collection_report'),
]
