from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import County, LoanApplication, Payment, LoanDisbursement


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_id', 'user_link', 'status_badge', 'requested_amount', 
        'repayment_period', 'created_at', 'admin_actions'
    ]
    list_filter = ['status', 'gender', 'marital_status', 'county', 'created_at', 'approved_at']
    search_fields = ['application_id', 'user__username', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['application_id', 'created_at', 'updated_at', 'submitted_at', 'approved_at', 'disbursed_at']
    ordering = ['-created_at']
    list_per_page = 25
    
    actions = ['approve_loans', 'reject_loans', 'mark_as_disbursed']
    
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
    
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'secondary',
            'submitted': 'info',
            'under_review': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'disbursed': 'primary',
            'completed': 'success'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def admin_actions(self, obj):
        links = []
        if obj.status == 'submitted':
            links.append(f'<a href="#" onclick="approveLoan(\'{obj.application_id}\')" class="btn btn-sm btn-success">Approve</a>')
        if obj.status in ['draft', 'submitted', 'under_review']:
            links.append(f'<a href="#" onclick="rejectLoan(\'{obj.application_id}\')" class="btn btn-sm btn-danger">Reject</a>')
        if obj.status == 'approved':
            links.append(f'<a href="#" onclick="disburseLoan(\'{obj.application_id}\')" class="btn btn-sm btn-primary">Disburse</a>')
        return mark_safe(' '.join(links))
    admin_actions.short_description = 'Actions'
    
    def approve_loans(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} loan(s) were successfully approved.')
    approve_loans.short_description = "Approve selected loans"
    
    def reject_loans(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} loan(s) were successfully rejected.')
    reject_loans.short_description = "Reject selected loans"
    
    def mark_as_disbursed(self, request, queryset):
        updated = queryset.update(status='disbursed')
        self.message_user(request, f'{updated} loan(s) were successfully marked as disbursed.')
    mark_as_disbursed.short_description = "Mark selected loans as disbursed"
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'loan_application_link', 'amount', 'payment_method', 'status_badge', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['reference_number', 'loan_application__application_id', 'transaction_id']
    readonly_fields = ['reference_number', 'payment_date']
    ordering = ['-payment_date']
    list_per_page = 25
    
    def loan_application_link(self, obj):
        if obj.loan_application:
            url = reverse('admin:loans_loanapplication_change', args=[obj.loan_application.id])
            return format_html('<a href="{}">{}</a>', url, obj.loan_application.application_id)
        return '-'
    loan_application_link.short_description = 'Loan Application'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(LoanDisbursement)
class LoanDisbursementAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'loan_application_link', 'amount', 'disbursement_method', 'disbursement_date']
    list_filter = ['disbursement_method', 'disbursement_date']
    search_fields = ['reference_number', 'loan_application__application_id', 'transaction_id']
    readonly_fields = ['reference_number', 'disbursement_date']
    ordering = ['-disbursement_date'] 
    list_per_page = 25
    
    def loan_application_link(self, obj):
        if obj.loan_application:
            url = reverse('admin:loans_loanapplication_change', args=[obj.loan_application.id])
            return format_html('<a href="{}">{}</a>', url, obj.loan_application.application_id)
        return '-'
    loan_application_link.short_description = 'Loan Application' 