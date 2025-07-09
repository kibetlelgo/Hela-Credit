from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count, Q
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import datetime, timedelta
from .models import County, LoanApplication, Payment, LoanDisbursement


class StatusFilter(SimpleListFilter):
    title = 'Application Status'
    parameter_name = 'status_filter'

    def lookups(self, request, model_admin):
        return (
            ('pending_review', 'Pending Review'),
            ('approved_rejected', 'Approved/Rejected'),
            ('active_loans', 'Active Loans'),
            ('completed', 'Completed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'pending_review':
            return queryset.filter(status__in=['submitted', 'under_review'])
        elif self.value() == 'approved_rejected':
            return queryset.filter(status__in=['approved', 'rejected'])
        elif self.value() == 'active_loans':
            return queryset.filter(status__in=['approved', 'disbursed'])
        elif self.value() == 'completed':
            return queryset.filter(status='completed')


class DateRangeFilter(SimpleListFilter):
    title = 'Application Date'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('quarter', 'This Quarter'),
            ('year', 'This Year'),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()
        if self.value() == 'today':
            return queryset.filter(created_at__date=today)
        elif self.value() == 'week':
            week_start = today - timedelta(days=today.weekday())
            return queryset.filter(created_at__date__gte=week_start)
        elif self.value() == 'month':
            return queryset.filter(created_at__month=today.month, created_at__year=today.year)
        elif self.value() == 'quarter':
            quarter_start = today.replace(day=1)
            if today.month in [4, 5, 6]:
                quarter_start = quarter_start.replace(month=4)
            elif today.month in [7, 8, 9]:
                quarter_start = quarter_start.replace(month=7)
            elif today.month in [10, 11, 12]:
                quarter_start = quarter_start.replace(month=10)
            else:
                quarter_start = quarter_start.replace(month=1)
            return queryset.filter(created_at__date__gte=quarter_start)
        elif self.value() == 'year':
            return queryset.filter(created_at__year=today.year)


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'loan_count']
    search_fields = ['name']
    ordering = ['name']
    
    def loan_count(self, obj):
        return obj.loanapplication_set.count()
    loan_count.short_description = 'Total Loans'


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'application_id', 'user_info', 'status_badge', 'amount_info', 
        'repayment_info', 'created_date', 'action_buttons'
    ]
    list_filter = [
        StatusFilter, DateRangeFilter, 'status', 'gender', 'marital_status', 
        'county', 'employment_status', 'education_level', 'created_at'
    ]
    search_fields = [
        'application_id', 'user__username', 'user__first_name', 'user__last_name', 
        'user__email', 'phone_number', 'id_number'
    ]
    readonly_fields = [
        'application_id', 'created_at', 'updated_at', 'submitted_at', 
        'approved_at', 'disbursed_at', 'monthly_payment', 'total_interest', 
        'total_amount', 'payment_summary'
    ]
    ordering = ['-created_at']
    list_per_page = 25
    actions = ['approve_applications', 'reject_applications', 'mark_disbursed', 'export_to_csv']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('application_id', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Personal Information', {
            'fields': (
                'phone_number', 'id_number', 'gender', 'date_of_birth', 
                'marital_status', 'county', 'next_of_kin', 'next_of_kin_phone',
                'education_level', 'employment_status', 'monthly_income', 'loan_purpose'
            )
        }),
        ('Loan Details', {
            'fields': (
                'requested_amount', 'approved_amount', 'repayment_period', 
                'interest_rate', 'monthly_payment', 'total_interest', 'total_amount'
            )
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'mpesa_number', 'bank_account')
        }),
        ('Timeline', {
            'fields': ('submitted_at', 'approved_at', 'disbursed_at'),
            'classes': ('collapse',)
        }),
        ('Payment Summary', {
            'fields': ('payment_summary',),
            'classes': ('collapse',)
        }),
    )

    def user_info(self, obj):
        return format_html(
            '<div><strong>{}</strong><br><small>{}</small><br><small>{}</small></div>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email,
            obj.phone_number
        )
    user_info.short_description = 'User Information'

    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'submitted': '#007bff',
            'under_review': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'disbursed': '#17a2b8',
            'completed': '#6f42c1',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def amount_info(self, obj):
        if obj.approved_amount:
            return format_html(
                '<div><strong>KES {}</strong><br><small>Approved: KES {}</small></div>',
                obj.requested_amount,
                obj.approved_amount
            )
        return format_html('<strong>KES {}</strong>', obj.requested_amount)
    amount_info.short_description = 'Amount'

    def repayment_info(self, obj):
        return format_html(
            '<div><strong>{} months</strong><br><small>Monthly: KES {}</small></div>',
            obj.repayment_period,
            obj.monthly_payment
        )
    repayment_info.short_description = 'Repayment'

    def created_date(self, obj):
        return obj.created_at.strftime('%b %d, %Y')
    created_date.short_description = 'Created'

    def action_buttons(self, obj):
        links = []
        if obj.status in ['submitted', 'under_review']:
            links.append(f'<a href="?action=approve&id={obj.id}" class="btn btn-success btn-sm">Approve</a>')
            links.append(f'<a href="?action=reject&id={obj.id}" class="btn btn-danger btn-sm">Reject</a>')
        if obj.status == 'approved':
            links.append(f'<a href="?action=disburse&id={obj.id}" class="btn btn-info btn-sm">Disburse</a>')
        links.append(f'<a href="{reverse("admin:loans_loanapplication_change", args=[obj.id])}" class="btn btn-primary btn-sm">View</a>')
        return format_html(' '.join(links))
    action_buttons.short_description = 'Actions'

    def payment_summary(self, obj):
        payments = obj.payments.all()
        total_paid = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
        total_payments = payments.count()
        
        return format_html(
            '<div><strong>Total Paid: KES {}</strong><br>'
            '<small>Payments: {}</small><br>'
            '<small>Remaining: KES {}</small></div>',
            total_paid,
            total_payments,
            obj.total_amount - total_paid
        )
    payment_summary.short_description = 'Payment Summary'

    def approve_applications(self, request, queryset):
        updated = queryset.filter(status__in=['submitted', 'under_review']).update(
            status='approved',
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} applications have been approved.')
    approve_applications.short_description = 'Approve selected applications'

    def reject_applications(self, request, queryset):
        updated = queryset.filter(status__in=['submitted', 'under_review']).update(
            status='rejected'
        )
        self.message_user(request, f'{updated} applications have been rejected.')
    reject_applications.short_description = 'Reject selected applications'

    def mark_disbursed(self, request, queryset):
        updated = queryset.filter(status='approved').update(
            status='disbursed',
            disbursed_at=timezone.now()
        )
        self.message_user(request, f'{updated} loans have been marked as disbursed.')
    mark_disbursed.short_description = 'Mark selected loans as disbursed'

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="loan_applications.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Application ID', 'User', 'Status', 'Requested Amount', 'Approved Amount',
            'Repayment Period', 'Created Date', 'Phone Number', 'County'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.application_id,
                obj.user.get_full_name() or obj.user.username,
                obj.get_status_display(),
                obj.requested_amount,
                obj.approved_amount or '',
                obj.repayment_period,
                obj.created_at.strftime('%Y-%m-%d'),
                obj.phone_number,
                obj.county.name
            ])
        
        return response
    export_to_csv.short_description = 'Export selected applications to CSV'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'loan_link', 'amount', 'payment_method', 
        'status_badge', 'payment_date', 'user_info'
    ]
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = [
        'reference_number', 'loan_application__application_id', 
        'transaction_id', 'loan_application__user__username'
    ]
    readonly_fields = ['reference_number', 'payment_date']
    ordering = ['-payment_date']
    actions = ['mark_completed', 'mark_failed']

    def loan_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:loans_loanapplication_change', args=[obj.loan_application.id]),
            obj.loan_application.application_id
        )
    loan_link.short_description = 'Loan Application'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def user_info(self, obj):
        user = obj.loan_application.user
        return format_html(
            '<div><strong>{}</strong><br><small>{}</small></div>',
            user.get_full_name() or user.username,
            user.email
        )
    user_info.short_description = 'User'

    def mark_completed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='completed')
        self.message_user(request, f'{updated} payments have been marked as completed.')
    mark_completed.short_description = 'Mark selected payments as completed'

    def mark_failed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f'{updated} payments have been marked as failed.')
    mark_failed.short_description = 'Mark selected payments as failed'


@admin.register(LoanDisbursement)
class LoanDisbursementAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'loan_link', 'amount', 'disbursement_method', 
        'disbursement_date', 'user_info'
    ]
    list_filter = ['disbursement_method', 'disbursement_date']
    search_fields = [
        'reference_number', 'loan_application__application_id', 
        'transaction_id', 'loan_application__user__username'
    ]
    readonly_fields = ['reference_number', 'disbursement_date']
    ordering = ['-disbursement_date']

    def loan_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:loans_loanapplication_change', args=[obj.loan_application.id]),
            obj.loan_application.application_id
        )
    loan_link.short_description = 'Loan Application'

    def user_info(self, obj):
        user = obj.loan_application.user
        return format_html(
            '<div><strong>{}</strong><br><small>{}</small></div>',
            user.get_full_name() or user.username,
            user.email
        )
    user_info.short_description = 'User'


# Customize admin site
admin.site.site_header = "HelaCredit Administration"
admin.site.site_title = "HelaCredit Admin"
admin.site.index_title = "Welcome to HelaCredit Administration" 