from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from .models import LoanApplication, County, Payment, LoanDisbursement
from .forms import (
    LoanApplicationForm, PaymentForm, DisbursementForm, 
    LoanAmountForm, MpesaPaymentForm, BankTransferForm, MpesaServiceFeeForm, UserProfileForm
)
import uuid
from decimal import Decimal


def index(request):
    """Index page"""
    if request.user.is_authenticated:
        return redirect('loans:dashboard')
    return render(request, 'loans/index.html')


@login_required
def dashboard(request):
    """User dashboard"""
    try:
        active_loans = LoanApplication.objects.filter(
            user=request.user,
            status__in=['draft', 'submitted', 'under_review', 'approved', 'disbursed']
        ).order_by('-created_at')
        
        completed_loans = LoanApplication.objects.filter(
            user=request.user,
            status='completed'
        ).order_by('-created_at')[:5]
        
        # Calculate statistics
        total_applications = LoanApplication.objects.filter(user=request.user).count()
        completed_count = LoanApplication.objects.filter(user=request.user, status='completed').count()
        pending_count = LoanApplication.objects.filter(
            user=request.user, 
            status__in=['submitted', 'under_review', 'approved']
        ).count()
        
        context = {
            'active_loans': active_loans,
            'completed_loans': completed_loans,
            'total_applications': total_applications,
            'completed_count': completed_count,
            'pending_count': pending_count,
        }
        return render(request, 'loans/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'loans/dashboard.html')


@login_required
def apply_loan(request):
    """Loan application form"""
    try:
        if request.method == 'POST':
            form = LoanApplicationForm(request.POST)
            if form.is_valid():
                loan = form.save(commit=False)
                loan.user = request.user
                loan.application_id = uuid.uuid4()
                loan.save()
                messages.success(request, 'Loan application submitted successfully!')
                return redirect('loans:loan_details', application_id=loan.application_id)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = LoanApplicationForm()
        
        counties = County.objects.all().order_by('name')
        context = {
            'form': form,
            'counties': counties,
        }
        return render(request, 'loans/apply_loan.html', context)
    except Exception as e:
        messages.error(request, f'Error creating loan application: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def loan_details(request, application_id):
    """View loan application details"""
    try:
        loan = get_object_or_404(LoanApplication, application_id=application_id, user=request.user)
        service_fee = round(loan.requested_amount * Decimal('0.05'), 2)  # 5% service fee
        context = {
            'loan': loan,
            'service_fee': service_fee,
        }
        return render(request, 'loans/loan_details.html', context)
    except Exception as e:
        messages.error(request, f'Error loading loan details: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def edit_loan(request, application_id):
    """Edit loan application"""
    try:
        loan = get_object_or_404(LoanApplication, application_id=application_id, user=request.user)
        
        if loan.status not in ['draft']:
            messages.error(request, 'You can only edit draft applications.')
            return redirect('loans:loan_details', application_id=application_id)
        
        if request.method == 'POST':
            form = LoanApplicationForm(request.POST, instance=loan)
            if form.is_valid():
                form.save()
                messages.success(request, 'Loan application updated successfully!')
                return redirect('loans:loan_details', application_id=application_id)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = LoanApplicationForm(instance=loan)
        
        counties = County.objects.all().order_by('name')
        context = {
            'form': form,
            'loan': loan,
            'counties': counties,
        }
        return render(request, 'loans/edit_loan.html', context)
    except Exception as e:
        messages.error(request, f'Error editing loan application: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def submit_loan(request, application_id):
    """Submit loan application for review"""
    try:
        loan = get_object_or_404(LoanApplication, application_id=application_id, user=request.user)
        
        if loan.status != 'draft':
            messages.error(request, 'Only draft applications can be submitted.')
            return redirect('loans:loan_details', application_id=application_id)
        
        loan.status = 'submitted'
        loan.submitted_at = timezone.now()
        loan.save()
        
        messages.success(request, 'Loan application submitted for review!')
        return redirect('loans:service_fee_payment', application_id=application_id)
    except Exception as e:
        messages.error(request, f'Error submitting loan application: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def service_fee_payment(request, application_id):
    """Service fee payment page for M-Pesa"""
    try:
        loan = get_object_or_404(LoanApplication, application_id=application_id, user=request.user)
        
        if loan.status != 'submitted':
            messages.error(request, 'Service fee payment is only available for submitted applications.')
            return redirect('loans:loan_details', application_id=application_id)
        
        # Calculate service fee (5% of requested amount)
        service_fee = round(loan.requested_amount * Decimal('0.05'), 2)  # 5% service fee
        
        if request.method == 'POST':
            form = MpesaServiceFeeForm(request.POST)
            if form.is_valid():
                mpesa_code = form.cleaned_data['mpesa_transaction_code']
                
                # Create payment record
                payment = Payment.objects.create(
                    loan_application=loan,
                    amount=service_fee,
                    payment_method='mpesa',
                    reference_number=f"SF-{uuid.uuid4().hex[:8].upper()}",
                    status='completed',
                    transaction_id=mpesa_code
                )
                
                # Update loan status to under review
                loan.status = 'under_review'
                loan.save()
                
                messages.success(request, 'Service fee payment confirmed! Your application is now under review.')
                return redirect('loans:processing', application_id=application_id)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = MpesaServiceFeeForm()
        
        context = {
            'loan': loan,
            'service_fee': service_fee,
            'form': form,
            'mpesa_till': '5633760',
        }
        return render(request, 'loans/service_fee_payment.html', context)
    except Exception as e:
        messages.error(request, f'Error processing service fee payment: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def processing(request, application_id):
    """Processing page after service fee payment"""
    try:
        loan = get_object_or_404(LoanApplication, application_id=application_id, user=request.user)
        
        if loan.status not in ['under_review', 'approved', 'rejected']:
            messages.error(request, 'This page is only available for applications under review or processed.')
            return redirect('loans:loan_details', application_id=application_id)
        
        context = {
            'loan': loan,
        }
        return render(request, 'loans/processing.html', context)
    except Exception as e:
        messages.error(request, f'Error loading processing page: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def payment_page(request, application_id):
    """Payment page for loan processing fee"""
    try:
        loan = get_object_or_404(LoanApplication, application_id=application_id, user=request.user)
        
        if loan.status != 'approved':
            messages.error(request, 'Payment is only available for approved loans.')
            return redirect('loans:loan_details', application_id=application_id)
        
        processing_fee = 500  # Fixed processing fee
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            
            if payment_method == 'mpesa':
                form = MpesaPaymentForm(request.POST)
                if form.is_valid():
                    mpesa_number = form.cleaned_data['mpesa_number']
                    # Here you would integrate with M-Pesa API
                    # For now, we'll simulate a successful payment
                    payment = Payment.objects.create(
                        loan_application=loan,
                        amount=processing_fee,
                        payment_method='mpesa',
                        reference_number=f"PAY-{uuid.uuid4().hex[:8].upper()}",
                        status='completed',
                        transaction_id=f"MPESA-{uuid.uuid4().hex[:8].upper()}"
                    )
                    messages.success(request, 'Payment processed successfully!')
                    return redirect('loans:disbursement_page', application_id=application_id)
            elif payment_method == 'bank_transfer':
                form = BankTransferForm(request.POST)
                if form.is_valid():
                    # Here you would handle bank transfer
                    payment = Payment.objects.create(
                        loan_application=loan,
                        amount=processing_fee,
                        payment_method='bank_transfer',
                        reference_number=f"PAY-{uuid.uuid4().hex[:8].upper()}",
                        status='pending'
                    )
                    messages.success(request, 'Bank transfer initiated. Please complete the transfer.')
                    return redirect('loans:loan_details', application_id=application_id)
        else:
            mpesa_form = MpesaPaymentForm()
            bank_form = BankTransferForm()
        
        context = {
            'loan': loan,
            'processing_fee': processing_fee,
            'mpesa_form': mpesa_form,
            'bank_form': bank_form,
        }
        return render(request, 'loans/payment_page.html', context)
    except Exception as e:
        messages.error(request, f'Error processing payment: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def disbursement_page(request, application_id):
    """Loan disbursement page"""
    try:
        loan = get_object_or_404(LoanApplication, application_id=application_id, user=request.user)
        
        # Check if payment has been made
        payment = Payment.objects.filter(loan_application=loan, status='completed').first()
        if not payment:
            messages.error(request, 'Please complete the payment first.')
            return redirect('loans:payment_page', application_id=application_id)
        
        if request.method == 'POST':
            form = DisbursementForm(request.POST)
            if form.is_valid():
                disbursement = form.save(loan_application=loan)
                loan.status = 'disbursed'
                loan.disbursed_at = timezone.now()
                loan.save()
                
                messages.success(request, 'Loan disbursed successfully!')
                return redirect('loans:loan_details', application_id=application_id)
        else:
            form = DisbursementForm()
        
        context = {
            'loan': loan,
            'form': form,
        }
        return render(request, 'loans/disbursement_page.html', context)
    except Exception as e:
        messages.error(request, f'Error processing disbursement: {str(e)}')
        return redirect('loans:dashboard')


@login_required
def loan_history(request):
    """User's loan history with filtering and statistics"""
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        date_filter = request.GET.get('date', '')
        
        # Base queryset
        loans = LoanApplication.objects.filter(user=request.user)
        
        # Apply filters
        if status_filter:
            loans = loans.filter(status=status_filter)
        
        if date_filter:
            if date_filter == 'this_month':
                loans = loans.filter(created_at__month=timezone.now().month, created_at__year=timezone.now().year)
            elif date_filter == 'last_month':
                last_month = timezone.now().replace(day=1) - timezone.timedelta(days=1)
                loans = loans.filter(created_at__month=last_month.month, created_at__year=last_month.year)
            elif date_filter == 'this_year':
                loans = loans.filter(created_at__year=timezone.now().year)
        
        # Order by creation date (newest first)
        loans = loans.order_by('-created_at')
        
        # Calculate statistics
        total_loans = LoanApplication.objects.filter(user=request.user).count()
        total_requested = sum(loan.requested_amount for loan in loans)
        total_approved = sum(loan.approved_amount or 0 for loan in loans)
        
        # Status counts
        status_counts = {}
        status_data = []
        for status, label in LoanApplication.STATUS_CHOICES:
            count = LoanApplication.objects.filter(user=request.user, status=status).count()
            status_counts[status] = count
            if count > 0:
                status_data.append({
                    'code': status,
                    'label': label,
                    'count': count
                })
        
        # Get recent loans for quick access
        recent_loans = loans[:5]
        
        context = {
            'loans': loans,
            'recent_loans': recent_loans,
            'total_loans': total_loans,
            'total_requested': total_requested,
            'total_approved': total_approved,
            'status_counts': status_counts,
            'status_data': status_data,
            'status_filter': status_filter,
            'date_filter': date_filter,
            'status_choices': LoanApplication.STATUS_CHOICES,
        }
        return render(request, 'loans/loan_history.html', context)
    except Exception as e:
        messages.error(request, f'Error loading loan history: {str(e)}')
        return render(request, 'loans/loan_history.html')


@login_required
def profile(request):
    """User profile page - view and edit personal information"""
    try:
        # Get user's latest loan application for profile data
        latest_loan = LoanApplication.objects.filter(user=request.user).order_by('-created_at').first()
        
        if request.method == 'POST':
            form = UserProfileForm(request.POST, user=request.user)
            if form.is_valid():
                # Update Django User model fields
                user = request.user
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.save()
                
                # Update or create loan application with profile data
                if latest_loan:
                    # Update existing loan application
                    latest_loan.phone_number = form.cleaned_data['phone_number']
                    latest_loan.id_number = form.cleaned_data['id_number']
                    latest_loan.gender = form.cleaned_data['gender']
                    latest_loan.date_of_birth = form.cleaned_data['date_of_birth']
                    latest_loan.marital_status = form.cleaned_data['marital_status']
                    latest_loan.county = form.cleaned_data['county']
                    latest_loan.next_of_kin = form.cleaned_data['next_of_kin']
                    latest_loan.next_of_kin_phone = form.cleaned_data['next_of_kin_phone']
                    latest_loan.education_level = form.cleaned_data['education_level']
                    latest_loan.save()
                else:
                    # Create a new draft loan application with profile data
                    LoanApplication.objects.create(
                        user=request.user,
                        phone_number=form.cleaned_data['phone_number'],
                        id_number=form.cleaned_data['id_number'],
                        gender=form.cleaned_data['gender'],
                        date_of_birth=form.cleaned_data['date_of_birth'],
                        marital_status=form.cleaned_data['marital_status'],
                        county=form.cleaned_data['county'],
                        next_of_kin=form.cleaned_data['next_of_kin'],
                        next_of_kin_phone=form.cleaned_data['next_of_kin_phone'],
                        education_level=form.cleaned_data['education_level'],
                        requested_amount=1000,  # Default amount
                        repayment_period=12,  # Default period
                        status='draft'
                    )
                
                messages.success(request, 'Profile updated successfully!')
                return redirect('loans:profile')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = UserProfileForm(user=request.user)
        
        # Get user statistics
        total_loans = LoanApplication.objects.filter(user=request.user).count()
        active_loans = LoanApplication.objects.filter(
            user=request.user,
            status__in=['draft', 'submitted', 'under_review', 'approved', 'disbursed']
        ).count()
        completed_loans = LoanApplication.objects.filter(
            user=request.user,
            status='completed'
        ).count()
        
        context = {
            'form': form,
            'latest_loan': latest_loan,
            'total_loans': total_loans,
            'active_loans': active_loans,
            'completed_loans': completed_loans,
        }
        return render(request, 'loans/profile.html', context)
    except Exception as e:
        messages.error(request, f'Error loading profile: {str(e)}')
        return render(request, 'loans/profile.html')


@require_http_methods(["POST"])
@login_required
def calculate_loan(request):
    """AJAX endpoint for loan calculations"""
    try:
        amount = float(request.POST.get('amount', 0))
        period = int(request.POST.get('period', 12))
        interest_rate = 8.0  # 8% annual interest rate
        
        monthly_rate = (interest_rate / 100) / 12
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** period) / ((1 + monthly_rate) ** period - 1)
        total_interest = (monthly_payment * period) - amount
        total_amount = amount + total_interest
        
        return JsonResponse({
            'monthly_payment': round(monthly_payment, 2),
            'total_interest': round(total_interest, 2),
            'total_amount': round(total_amount, 2),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 