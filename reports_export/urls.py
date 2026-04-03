from django.urls import path
from reports_export import views

urlpatterns = [
    path('ledger/<int:member_id>/', views.member_ledger, name='member_ledger'),
]
