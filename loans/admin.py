from django.contrib import admin
from .models import County, LoanApplication, Payment, LoanDisbursement


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_id', 'user', 'status', 'requested_amount', 
        'repayment_period', 'created_at'
    ]
    list_filter = ['status', 'gender', 'marital_status', 'county', 'created_at']
    search_fields = ['application_id', 'user__username', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['application_id', 'created_at', 'updated_at', 'submitted_at', 'approved_at', 'disbursed_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('application_id', 'user', 'status')
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'id_number', 'gender', 'date_of_birth', 'marital_status', 'county')
        }),
        ('Loan Details', {
            'fields': ('requested_amount', 'approved_amount', 'repayment_period', 'interest_rate')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'mpesa_number', 'bank_account')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'approved_at', 'disbursed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'loan_application', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['reference_number', 'loan_application__application_id', 'transaction_id']
    readonly_fields = ['reference_number', 'payment_date']
    ordering = ['-payment_date']


@admin.register(LoanDisbursement)
class LoanDisbursementAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'loan_application', 'amount', 'disbursement_method', 'disbursement_date']
    list_filter = ['disbursement_method', 'disbursement_date']
    search_fields = ['reference_number', 'loan_application__application_id', 'transaction_id']
    readonly_fields = ['reference_number', 'disbursement_date']
    ordering = ['-disbursement_date'] 