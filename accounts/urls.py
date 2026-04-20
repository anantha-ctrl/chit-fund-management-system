from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reports/', views.reports_view, name='reports'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('profile/', views.profile_view, name='profile_view'),
    path('my-chits/', views.my_chits_view, name='my_chits'),
    path('my-chits/<int:mc_id>/passbook/', views.customer_passbook_view, name='customer_passbook'),
    path('my-payments/', views.customer_payment_history_view, name='customer_payment_history'),
    path('my-reports/', views.customer_reports_view, name='customer_reports'),
    path('update-preferences/', views.update_preferences_view, name='update_preferences'),
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('my-documents/', views.customer_documents_view, name='customer_documents'),
    path('documents/<int:pk>/<str:action>/', views.admin_approve_document, name='admin_approve_document'),
    
    # Password Reset (OTP Flow)
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('otp-verify/', views.otp_verify_view, name='otp_verify'),
    path('password-reset-confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # 2FA URLs
    path('2fa/enable/', views.enable_2fa_view, name='enable_2fa'),
    path('2fa/verify/', views.verify_2fa_view, name='verify_2fa'),
    path('pay/', views.customer_pay_view, name='customer_pay'),
    path('payment/success/', views.customer_payment_success, name='customer_payment_success'),
    path('api/search/', views.global_search_api, name='global_search_api'),
]

