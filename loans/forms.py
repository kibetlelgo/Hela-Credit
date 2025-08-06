from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import LoanApplication, County, Payment, LoanDisbursement
import uuid


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(
        required=True, 
        help_text='',  # Remove email validation instructions
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='',  # Remove first name instructions
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='',  # Remove last name instructions
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text for username field
        self.fields['username'].help_text = ''  # Remove username validation instructions
        
        # Add Bootstrap classes to password fields and remove help text
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password1'].help_text = ''  # Remove password validation instructions
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        self.fields['password2'].help_text = ''  # Remove password confirmation instructions
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email


class LoanApplicationForm(forms.ModelForm):
    """Form for loan application"""
    INCOME_CHOICES = [
        ('0-9999', 'Below 10,000 Ksh'),
        ('10000-19999', '10,000 - 20,000 Ksh'),
        ('20000-29999', '20,000 - 30,000 Ksh'),
        ('30000-49999', '30,000 - 50,000 Ksh'),
        ('50000-99999', '50,000 - 100,000 Ksh'),
        ('100000+', 'Above 100,000 Ksh'),
    ]
    
    LOAN_PURPOSE_CHOICES = [
        ('business', 'Business'),
        ('school_fees', 'School Fees'),
        ('medical', 'Medical'),
        ('emergency', 'Emergency'),
        ('personal', 'Personal'),
    ]
    
    class Meta:
        model = LoanApplication
        fields = [
            'phone_number', 'id_number', 'gender', 'date_of_birth', 
            'marital_status', 'county', 'next_of_kin', 'next_of_kin_phone', 
            'education_level', 'employment_status', 'monthly_income', 'loan_purpose',
            'requested_amount', 'repayment_period'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'requested_amount': forms.NumberInput(attrs={'min': '1000', 'step': '100'}),
            'repayment_period': forms.NumberInput(attrs={'min': '1', 'max': '60'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError('Please enter a valid 10-digit phone number.')
        return phone
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if not id_number.isdigit() or len(id_number) != 8:
            raise forms.ValidationError('Please enter a valid 8-digit ID number.')
        return id_number
    
    def clean_next_of_kin_phone(self):
        phone = self.cleaned_data.get('next_of_kin_phone')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError('Please enter a valid 10-digit phone number for next of kin.')
        return phone

    monthly_income = forms.ChoiceField(
        choices=[('', '')] + INCOME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Monthly Income (KES)'
    )

    loan_purpose = forms.ChoiceField(
        choices=[('', '')] + LOAN_PURPOSE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Loan Purpose'
    )

    repayment_period = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        widget=forms.Select(
            choices=[('', '')] + [(i, f"{i} months") for i in range(1, 61)],
            attrs={'class': 'form-control'}
        )
    )

    education_level = forms.ChoiceField(
        choices=[('', '')] + LoanApplication.EDUCATION_LEVEL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select your highest level of education"
    )
    employment_status = forms.ChoiceField(
        choices=[('', '')] + LoanApplication.EMPLOYMENT_STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    gender = forms.ChoiceField(
        choices=[('', '')] + LoanApplication.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    marital_status = forms.ChoiceField(
        choices=[('', '')] + LoanApplication.MARITAL_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    county = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        empty_label='',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    next_of_kin = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    next_of_kin_phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )


class PaymentForm(forms.ModelForm):
    """Form for loan payments"""
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': '100', 'step': '100'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, loan_application, commit=True):
        payment = super().save(commit=False)
        payment.loan_application = loan_application
        payment.reference_number = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        
        if commit:
            payment.save()
        return payment


class DisbursementForm(forms.ModelForm):
    """Form for loan disbursement"""
    class Meta:
        model = LoanDisbursement
        fields = ['disbursement_method']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, loan_application, commit=True):
        disbursement = super().save(commit=False)
        disbursement.loan_application = loan_application
        disbursement.amount = loan_application.approved_amount or loan_application.requested_amount
        disbursement.reference_number = f"DIS-{uuid.uuid4().hex[:8].upper()}"
        
        if commit:
            disbursement.save()
        return disbursement


class LoanAmountForm(forms.Form):
    """Form for loan amount selection"""
    requested_amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(1000)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1000',
            'step': '100',
            'placeholder': 'Enter loan amount'
        })
    )
    repayment_period = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        widget=forms.Select(
            choices=[(i, f"{i} months") for i in range(1, 61)],
            attrs={'class': 'form-control'}
        )
    )


class MpesaPaymentForm(forms.Form):
    """Form for M-Pesa payment details"""
    mpesa_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter M-Pesa number '
        })
    )
    
    def clean_mpesa_number(self):
        mpesa_number = self.cleaned_data.get('mpesa_number')
        if not mpesa_number.isdigit() or len(mpesa_number) != 10:
            raise forms.ValidationError('Please enter a valid 10-digit M-Pesa number.')
        return mpesa_number


class BankTransferForm(forms.Form):
    """Form for bank transfer details"""
    bank_account = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter bank account number'
        })
    )
    bank_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter bank name'
        })
    )


class MpesaServiceFeeForm(forms.Form):
    """Form for M-Pesa service fee payment"""
    mpesa_transaction_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter M-Pesa transaction code',
            'pattern': '[A-Z0-9]+',
            'title': 'Enter the transaction code from your M-Pesa message'
        }),
        help_text="Enter the transaction code from your M-Pesa confirmation message"
    )
    
    def clean_mpesa_transaction_code(self):
        code = self.cleaned_data['mpesa_transaction_code']
        if not code:
            raise forms.ValidationError("Transaction code is required to proceed.")
        # Remove any spaces and convert to uppercase
        code = code.replace(' ', '').upper()
        if len(code) < 8:
            raise forms.ValidationError("Transaction code appears to be too short.")
        return code


class UserProfileForm(forms.ModelForm):
    """Form for user profile editing"""
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    id_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your national ID number'
        }),
        help_text="Enter your national ID number"
    )
    gender = forms.ChoiceField(
        choices=LoanApplication.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    marital_status = forms.ChoiceField(
        choices=LoanApplication.MARITAL_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    county = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        empty_label='',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    next_of_kin = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    next_of_kin_phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    education_level = forms.ChoiceField(
        choices=LoanApplication.EDUCATION_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employment_status = forms.ChoiceField(
        choices=LoanApplication.EMPLOYMENT_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = LoanApplication
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'id_number',
            'gender', 'date_of_birth', 'marital_status', 'county',
            'next_of_kin', 'next_of_kin_phone', 'education_level'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Pre-populate Django User fields
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            
            # Get the most recent loan application for this user to pre-populate other fields
            try:
                latest_loan = LoanApplication.objects.filter(user=user).order_by('-created_at').first()
                if latest_loan:
                    self.fields['phone_number'].initial = latest_loan.phone_number
                    self.fields['id_number'].initial = latest_loan.id_number
                    self.fields['gender'].initial = latest_loan.gender
                    self.fields['date_of_birth'].initial = latest_loan.date_of_birth
                    self.fields['marital_status'].initial = latest_loan.marital_status
                    self.fields['county'].initial = latest_loan.county
                    self.fields['next_of_kin'].initial = latest_loan.next_of_kin
                    self.fields['next_of_kin_phone'].initial = latest_loan.next_of_kin_phone
                    self.fields['education_level'].initial = latest_loan.education_level
            except:
                pass


class LoanApplicantInfoForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = [
            'phone_number', 'id_number', 'gender', 'date_of_birth',
            'marital_status', 'county', 'next_of_kin', 'next_of_kin_phone'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class LoanDetailsForm(forms.ModelForm):
    INCOME_CHOICES = [
        ('0-9999', 'Below 10,000 Ksh'),
        ('10000-19999', '10,000 - 20,000 Ksh'),
        ('20000-29999', '20,000 - 30,000 Ksh'),
        ('30000-49999', '30,000 - 50,000 Ksh'),
        ('50000-99999', '50,000 - 100,000 Ksh'),
        ('100000+', 'Above 100,000 Ksh'),
    ]
    LOAN_PURPOSE_CHOICES = [
        ('business', 'Business'),
        ('school_fees', 'School Fees'),
        ('medical', 'Medical'),
        ('emergency', 'Emergency'),
        ('personal', 'Personal'),
    ]
    REQUESTED_AMOUNT_CHOICES = [
        ('', ''),
        ('5000',  'Limit Ksh 5000  - (Savings amount: Ksh 190)'),
        ('10000', 'Limit Ksh 10000 - (Savings amount: Ksh 280)'),
        ('15000', 'Limit Ksh 15000 - (Savings amount: Ksh 350)'),
        ('20000', 'Limit Ksh 20000 - (Savings amount: Ksh 465)'),
        ('30000', 'Limit Ksh 30000 - (Savings amount: Ksh 530)'),
        ('40000', 'Limit Ksh 40000 - (Savings amount: Ksh 645)'),
        ('50000', 'Limit Ksh 50000 - (Savings amount: Ksh 755)'),  
    ]
    requested_amount = forms.ChoiceField(
        choices=REQUESTED_AMOUNT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Loan Limit'
    )
    monthly_income = forms.ChoiceField(
        choices=[('', '')] + INCOME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Monthly Income (KES)'
    )
    loan_purpose = forms.ChoiceField(
        choices=[('', '')] + LOAN_PURPOSE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Loan Purpose'
    )
    repayment_period = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)],
        widget=forms.Select(
            choices=[('', '')] + [(i, f"{i} months") for i in range(1, 13)],
            attrs={'class': 'form-control'}
        )
    )
    education_level = forms.ChoiceField(
        choices=[('', '')] + LoanApplication.EDUCATION_LEVEL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select your highest level of education"
    )
    employment_status = forms.ChoiceField(
        choices=[('', '')] + LoanApplication.EMPLOYMENT_STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    # Removed gender, marital_status, county, next_of_kin, next_of_kin_phone
    class Meta:
        model = LoanApplication
        fields = [
            'education_level', 'employment_status', 'monthly_income', 'loan_purpose',
            'requested_amount', 'repayment_period'
        ]
        widgets = {
            'repayment_period': forms.NumberInput(attrs={'min': '1', 'max': '60'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['monthly_income', 'loan_purpose']:
                field.widget.attrs.update({'class': 'form-control'}) 