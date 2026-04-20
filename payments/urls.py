from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('create/', views.payment_create, name='payment_create'),
    path('<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('<int:pk>/receipt/', views.payment_receipt, name='chit_payment_receipt'),
    path('bulk-reminders/', views.bulk_reminder_view, name='bulk_reminders'),
    path('field-collection/', views.field_collection_view, name='field_collection'),
    path('my-collections/', views.staff_collection_report_view, name='staff_report'),
    path('handover/initiate/', views.initiate_handover, name='initiate_handover'),
    path('handovers/', views.handover_list_view, name='handover_list'),
    path('handovers/<int:pk>/approve/', views.approve_handover_view, name='approve_handover'),
    path('handovers/<int:pk>/reject/', views.reject_handover_view, name='reject_handover'),
    path('follow-up/add/', views.add_follow_up, name='add_follow_up'),
    path('follow-up/<int:pk>/complete/', views.complete_follow_up, name='complete_follow_up'),
    # Payment Verification System
    path('submit-proof/<int:payment_id>/', views.customer_submit_proof, name='customer_submit_proof'),
    path('verifications/', views.admin_proof_list, name='admin_proof_list'),
    path('verifications/<int:pk>/<str:action>/', views.admin_process_proof, name='admin_process_proof'),
    path('manage-qr/', views.manage_payment_qr, name='manage_payment_qr'),
    path('api/predict-next/', views.get_payment_prediction, name='predict_payment'),
]
