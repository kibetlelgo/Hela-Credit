from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import LoanApplication, Payment, County


@staff_member_required
def admin_dashboard(request):
    """Custom admin dashboard with statistics"""
    
    # Get date ranges
    today = timezone.now().date()
    this_month = today.replace(day=1)
    this_year = today.replace(month=1, day=1)
    
    # Loan Application Statistics
    total_applications = LoanApplication.objects.count()
    applications_this_month = LoanApplication.objects.filter(created_at__date__gte=this_month).count()
    applications_this_year = LoanApplication.objects.filter(created_at__date__gte=this_year).count()
    
    # Status breakdown
    status_counts = LoanApplication.objects.values('status').annotate(count=Count('id'))
    status_data = {item['status']: item['count'] for item in status_counts}
    
    # Amount statistics
    total_requested = LoanApplication.objects.aggregate(total=Sum('requested_amount'))['total'] or 0
    total_approved = LoanApplication.objects.filter(status__in=['approved', 'disbursed', 'completed']).aggregate(total=Sum('approved_amount'))['total'] or 0
    
    # Payment statistics
    total_payments = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    payments_this_month = Payment.objects.filter(
        status='completed',
        payment_date__date__gte=this_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent activity
    recent_applications = LoanApplication.objects.select_related('user', 'county').order_by('-created_at')[:10]
    recent_payments = Payment.objects.select_related('loan_application__user').order_by('-payment_date')[:10]
    
    # County statistics
    county_stats = County.objects.annotate(
        application_count=Count('loanapplication'),
        total_amount=Sum('loanapplication__requested_amount')
    ).order_by('-application_count')[:10]
    
    # Monthly trends (last 12 months)
    monthly_trends = []
    for i in range(12):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = month_start.replace(day=28) + timedelta(days=4)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        count = LoanApplication.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    monthly_trends.reverse()
    
    context = {
        'total_applications': total_applications,
        'applications_this_month': applications_this_month,
        'applications_this_year': applications_this_year,
        'status_data': status_data,
        'total_requested': total_requested,
        'total_approved': total_approved,
        'total_payments': total_payments,
        'payments_this_month': payments_this_month,
        'recent_applications': recent_applications,
        'recent_payments': recent_payments,
        'county_stats': county_stats,
        'monthly_trends': monthly_trends,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def loan_analytics(request):
    """Detailed loan analytics"""
    
    # Filter parameters
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    county_filter = request.GET.get('county', '')
    
    # Base queryset
    queryset = LoanApplication.objects.select_related('user', 'county')
    
    # Apply filters
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
    
    if county_filter:
        queryset = queryset.filter(county_id=county_filter)
    
    # Analytics data
    total_count = queryset.count()
    total_amount = queryset.aggregate(total=Sum('requested_amount'))['total'] or 0
    avg_amount = total_amount / total_count if total_count > 0 else 0
    
    # Status distribution
    status_distribution = queryset.values('status').annotate(
        count=Count('id'),
        total_amount=Sum('requested_amount')
    ).order_by('-count')
    
    # County distribution
    county_distribution = queryset.values('county__name').annotate(
        count=Count('id'),
        total_amount=Sum('requested_amount')
    ).order_by('-count')
    
    # Monthly distribution
    monthly_distribution = queryset.extra(
        select={'month': "DATE_FORMAT(created_at, '%%Y-%%m')"}
    ).values('month').annotate(
        count=Count('id'),
        total_amount=Sum('requested_amount')
    ).order_by('month')
    
    # Get all counties for filter
    counties = County.objects.all().order_by('name')
    
    context = {
        'queryset': queryset,
        'total_count': total_count,
        'total_amount': total_amount,
        'avg_amount': avg_amount,
        'status_distribution': status_distribution,
        'county_distribution': county_distribution,
        'monthly_distribution': monthly_distribution,
        'counties': counties,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'county_filter': county_filter,
    }
    
    return render(request, 'admin/analytics.html', context) 