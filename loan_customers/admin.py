from django.contrib import admin
from .models import LoanAgent


@admin.register(LoanAgent)
class LoanAgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_code', 'branch', 'phone', 'is_active']
    list_filter = ['branch', 'is_active']
    search_fields = ['user__username', 'employee_code', 'phone']
