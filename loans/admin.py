from django.contrib import admin
from .models import Loan, EMISchedule


class EMIScheduleInline(admin.TabularInline):
    model = EMISchedule
    extra = 0
    readonly_fields = ['installment_number', 'due_date', 'emi_amount',
                       'principal_component', 'interest_component',
                       'opening_balance', 'closing_balance',
                       'paid_amount', 'status']
    can_delete = False


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_number', 'customer', 'loan_amount', 'emi_amount',
                    'tenure_months', 'status', 'branch', 'created_at']
    list_filter = ['status', 'branch', 'interest_type', 'disbursement_mode']
    search_fields = ['loan_number', 'customer__full_name', 'customer__phone']
    readonly_fields = ['loan_number', 'emi_amount', 'total_interest',
                       'total_payable', 'outstanding_balance']
    date_hierarchy = 'created_at'
    inlines = [EMIScheduleInline]


@admin.register(EMISchedule)
class EMIScheduleAdmin(admin.ModelAdmin):
    list_display = ['loan', 'installment_number', 'due_date',
                    'emi_amount', 'paid_amount', 'status']
    list_filter = ['status']
    search_fields = ['loan__loan_number', 'loan__customer__full_name']
    date_hierarchy = 'due_date'
