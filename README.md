# HelaCredit - Modern Loan Application System

A modern, secure, and user-friendly loan application system built with Django. HelaCredit provides a complete solution for managing loan applications, payments, and disbursements.

## Features

### 🚀 Core Features
- **User Authentication**: Secure registration and login system
- **Loan Applications**: Complete loan application workflow
- **Payment Processing**: Support for M-Pesa and bank transfers
- **Loan Disbursement**: Automated loan disbursement system
- **Dashboard**: Comprehensive user dashboard with loan status
- **Admin Panel**: Full administrative control over applications

### 💳 Loan Management
- Multiple loan statuses (Draft, Submitted, Under Review, Approved, Rejected, Disbursed, Completed)
- Automatic loan calculations (monthly payments, interest, total amount)
- Flexible repayment periods (1-60 months)
- Competitive interest rates (8% annually)

### 🎨 User Experience
- Modern, responsive design with Bootstrap 5
- Interactive loan calculator
- Real-time status updates
- Mobile-friendly interface
- Intuitive navigation

### 🔒 Security
- Form validation and sanitization
- CSRF protection
- Secure password handling
- User session management

## Technology Stack

- **Backend**: Django 4.2.19
- **Database**: SQLite (production-ready with PostgreSQL)
- **Frontend**: Bootstrap 5, Font Awesome
- **Authentication**: Django's built-in auth system
- **Forms**: Django Forms with custom validation

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd helacredit
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Project Structure

```
helacredit/
├── accounts/                 # User authentication app
│   ├── views.py             # Authentication views
│   ├── urls.py              # Authentication URLs
│   └── templates/           # Auth templates
├── loans/                   # Main loan application app
│   ├── models.py            # Database models
│   ├── views.py             # Business logic views
│   ├── forms.py             # Form definitions
│   ├── admin.py             # Admin interface
│   └── templates/           # Loan templates
├── templates/               # Base templates
├── static/                  # Static files (CSS, JS, images)
├── manage.py               # Django management script
└── helacredit/             # Project settings
    ├── settings.py         # Django settings
    └── urls.py             # Main URL configuration
```

## Database Models

### LoanApplication
- User information and loan details
- Application status tracking
- Payment and disbursement information

### County
- Kenyan counties for location data

### Payment
- Payment records and transaction tracking

### LoanDisbursement
- Disbursement records and tracking

## Usage

### For Users
1. **Register/Login**: Create an account or sign in
2. **Apply for Loan**: Fill out the loan application form
3. **Submit Application**: Submit for review
4. **Make Payment**: Pay processing fee (if approved)
5. **Receive Loan**: Get disbursed to your account

### For Administrators
1. **Access Admin Panel**: Use superuser credentials
2. **Review Applications**: View and manage loan applications
3. **Update Status**: Change application status as needed
4. **Manage Users**: Handle user accounts and permissions

## API Endpoints

- `GET /` - Home page
- `GET /dashboard/` - User dashboard
- `GET /apply/` - Loan application form
- `GET /loan/<id>/` - Loan details
- `POST /calculate/` - Loan calculation API

## Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (set to False in production)
- `ALLOWED_HOSTS`: Allowed hostnames

### Database Configuration
The project uses SQLite by default. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'helacredit',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team.

## Roadmap

- [ ] M-Pesa API integration
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Advanced reporting
- [ ] Mobile app
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

---

**HelaCredit** - Making loans accessible, secure, and simple. 