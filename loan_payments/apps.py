from django.apps import AppConfig


class LoanPaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loan_payments'
    verbose_name = 'Loan Payments'

    def ready(self):
        import loan_payments.signals  # noqa: F401
