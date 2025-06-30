from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class County(models.Model):
    """Model for Kenyan counties"""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Counties"


class LoanApplication(models.Model):
    """Model for loan applications"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('diploma', 'Diploma'),
        ('degree', 'Bachelor\'s Degree'),
        ('masters', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
    ]
    
    # Application details
    application_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Personal information
    phone_number = models.CharField(max_length=15, help_text="Enter phone number (e.g., 0712345678)")
    id_number = models.CharField(max_length=20, help_text="Enter your national ID number")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    next_of_kin = models.CharField(max_length=100, help_text="Enter your next of kin's full name", null=True, blank=True)
    next_of_kin_phone = models.CharField(max_length=15, help_text="Enter next of kin's phone number (e.g., 0712345678)", null=True, blank=True)
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, help_text="Select your highest level of education", null=True, blank=True)
    
    # Loan details
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1000)])
    approved_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    repayment_period = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(60)], help_text="Repayment period in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=8.00, help_text="Annual interest rate (%)")
    
    # Payment information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    mpesa_number = models.CharField(max_length=15, null=True, blank=True)
    bank_account = models.CharField(max_length=50, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Loan Application {self.application_id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        elif self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        elif self.status == 'disbursed' and not self.disbursed_at:
            self.disbursed_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def monthly_payment(self):
        """Calculate monthly payment amount"""
        if self.approved_amount:
            principal = self.approved_amount
        else:
            principal = self.requested_amount
        
        monthly_rate = (self.interest_rate / 100) / 12
        if monthly_rate == 0:
            return principal / self.repayment_period
        
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** self.repayment_period) / ((1 + monthly_rate) ** self.repayment_period - 1)
        return round(monthly_payment, 2)
    
    @property
    def total_interest(self):
        """Calculate total interest to be paid"""
        if self.approved_amount:
            principal = self.approved_amount
        else:
            principal = self.requested_amount
        
        total_payment = self.monthly_payment * self.repayment_period
        return round(total_payment - principal, 2)
    
    @property
    def total_amount(self):
        """Calculate total amount to be repaid"""
        if self.approved_amount:
            principal = self.approved_amount
        else:
            principal = self.requested_amount
        
        return round(principal + self.total_interest, 2)


class Payment(models.Model):
    """Model for loan payments"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=LoanApplication.PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment {self.reference_number} - {self.loan_application.application_id}"


class LoanDisbursement(models.Model):
    """Model for loan disbursements"""
    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name='disbursement')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    disbursement_method = models.CharField(max_length=20, choices=LoanApplication.PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    disbursement_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Disbursement {self.reference_number} - {self.loan_application.application_id}" 