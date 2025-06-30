from django.core.management.base import BaseCommand
from django.db import connection
from loans.models import County

class Command(BaseCommand):
    help = 'Set up the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Setting up database...')
        
        # Create tables manually
        with connection.cursor() as cursor:
            # Create County table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans_county (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) UNIQUE NOT NULL
                )
            """)
            
            # Create LoanApplication table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans_loanapplication (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id VARCHAR(32) UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    phone_number VARCHAR(15) NOT NULL,
                    id_number VARCHAR(20) NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    date_of_birth DATE NOT NULL,
                    marital_status VARCHAR(10) NOT NULL,
                    requested_amount DECIMAL(10,2) NOT NULL,
                    approved_amount DECIMAL(10,2),
                    repayment_period INTEGER NOT NULL,
                    interest_rate DECIMAL(5,2) NOT NULL,
                    payment_method VARCHAR(20),
                    mpesa_number VARCHAR(15),
                    bank_account VARCHAR(50),
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    submitted_at DATETIME,
                    approved_at DATETIME,
                    disbursed_at DATETIME,
                    county_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES auth_user (id),
                    FOREIGN KEY (county_id) REFERENCES loans_county (id)
                )
            """)
            
            # Create Payment table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans_payment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loan_application_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_method VARCHAR(20) NOT NULL,
                    reference_number VARCHAR(100) UNIQUE NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    transaction_id VARCHAR(100),
                    payment_date DATETIME NOT NULL,
                    FOREIGN KEY (loan_application_id) REFERENCES loans_loanapplication (id)
                )
            """)
            
            # Create LoanDisbursement table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loans_loandisbursement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    loan_application_id INTEGER UNIQUE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    disbursement_method VARCHAR(20) NOT NULL,
                    reference_number VARCHAR(100) UNIQUE NOT NULL,
                    transaction_id VARCHAR(100),
                    disbursement_date DATETIME NOT NULL,
                    FOREIGN KEY (loan_application_id) REFERENCES loans_loanapplication (id)
                )
            """)
        
        # Populate counties
        counties = [
            'Mombasa', 'Kwale', 'Kilifi', 'Tana River', 'Lamu', 'Taita Taveta', 'Garissa', 'Wajir', 'Mandera', 'Marsabit',
            'Isiolo', 'Meru', 'Tharaka Nithi', 'Embu', 'Kitui', 'Machakos', 'Makueni', 'Nyandarua', 'Nyeri', 'Kirinyaga',
            'Murang\'a', 'Kiambu', 'Turkana', 'West Pokot', 'Samburu', 'Trans Nzoia', 'Uasin Gishu', 'Elgeyo Marakwet',
            'Nandi', 'Baringo', 'Laikipia', 'Nakuru', 'Narok', 'Kajiado', 'Kericho', 'Bomet', 'Kakamega', 'Vihiga',
            'Bungoma', 'Busia', 'Siaya', 'Kisumu', 'Homa Bay', 'Migori', 'Kisii', 'Nyamira', 'Nairobi'
        ]
        
        for county_name in counties:
            County.objects.get_or_create(name=county_name)
        
        self.stdout.write(self.style.SUCCESS('Database setup completed successfully!')) 