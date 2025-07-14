from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('apply/', views.apply_loan_step1, name='apply_loan'),
    path('apply/step2/', views.apply_loan_step2, name='apply_loan_step2'),
    path('contact/', views.contact, name='contact'),
    path('loan/<uuid:application_id>/', views.loan_details, name='loan_details'),
    path('loan/<uuid:application_id>/edit/', views.edit_loan, name='edit_loan'),
    path('loan/<uuid:application_id>/submit/', views.submit_loan, name='submit_loan'),
    path('loan/<uuid:application_id>/service-fee/', views.service_fee_payment, name='service_fee_payment'),
    path('loan/<uuid:application_id>/processing/', views.processing, name='processing'),
    path('loan/<uuid:application_id>/payment/', views.payment_page, name='payment_page'),
    path('loan/<uuid:application_id>/disbursement/', views.disbursement_page, name='disbursement_page'),
    path('history/', views.loan_history, name='loan_history'),
    path('calculate/', views.calculate_loan, name='calculate_loan'),
    path('mpesa/initiate/', views.initiate_stk_push, name='initiate_stk_push'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
] 