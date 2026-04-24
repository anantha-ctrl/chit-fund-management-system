from django.contrib import admin
from django.urls import path, include
from accounts.views import dashboard_view, landing_page
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('members/', include('members.urls')),
    path('chits/', include('chits.urls')),
    path('payments/', include('payments.urls')),
    path('auctions/', include('auctions.urls')),
    path('settlements/', include('settlements.urls')),
    path('branches/', include('branches.urls')),
    path('system/', include('system_settings.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports_export.urls')),
    # ── Loan Management System ──
    path('loan/', include('loans.urls')),
    path('loan/customers/', include('loan_customers.urls')),
    path('loan/payments/', include('loan_payments.urls')),
    path('loan/reports/', include('loan_reports.urls')),
    # ── Insurance Module ──
    # path('insurance/', include('insurance.urls')),
    # ── Documents Module ──
    # path('docs/', include('documents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
