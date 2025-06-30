# Generated manually

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Counties',
            },
        ),
        migrations.CreateModel(
            name='LoanApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted'), ('under_review', 'Under Review'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('disbursed', 'Disbursed'), ('completed', 'Completed')], default='draft', max_length=20)),
                ('phone_number', models.CharField(help_text='Enter phone number (e.g., 0712345678)', max_length=15)),
                ('id_number', models.CharField(help_text='Enter your national ID number', max_length=20)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('date_of_birth', models.DateField()),
                ('marital_status', models.CharField(choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed')], max_length=10)),
                ('requested_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(1000)])),
                ('approved_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('repayment_period', models.PositiveIntegerField(help_text='Repayment period in months', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(60)])),
                ('interest_rate', models.DecimalField(decimal_places=2, default=15.0, help_text='Annual interest rate (%)', max_digits=5)),
                ('payment_method', models.CharField(blank=True, choices=[('mpesa', 'M-Pesa'), ('bank_transfer', 'Bank Transfer')], max_length=20, null=True)),
                ('mpesa_number', models.CharField(blank=True, max_length=15, null=True)),
                ('bank_account', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('disbursed_at', models.DateTimeField(blank=True, null=True)),
                ('county', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loans.county')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_applications', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('mpesa', 'M-Pesa'), ('bank_transfer', 'Bank Transfer')], max_length=20)),
                ('reference_number', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('loan_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='loans.loanapplication')),
            ],
            options={
                'ordering': ['-payment_date'],
            },
        ),
        migrations.CreateModel(
            name='LoanDisbursement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('disbursement_method', models.CharField(choices=[('mpesa', 'M-Pesa'), ('bank_transfer', 'Bank Transfer')], max_length=20)),
                ('reference_number', models.CharField(max_length=100, unique=True)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('disbursement_date', models.DateTimeField(auto_now_add=True)),
                ('loan_application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='disbursement', to='loans.loanapplication')),
            ],
            options={
                'ordering': ['-disbursement_date'],
            },
        ),
    ] 