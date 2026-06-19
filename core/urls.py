from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('reports/summary/', views.reports_summary, name='reports_summary'),
    path('reports/tax-profit/', views.reports_tax_profit, name='reports_tax_profit'),
    
    # Super Admin URLs
    path('super-admin/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('super-admin/toggle-subscription/<int:business_id>/', views.toggle_subscription, name='toggle_subscription'),
    path('super-admin/add-business/', views.add_business_admin, name='add_business_admin'),
    path('super-admin/business/edit/<int:business_id>/', views.edit_business_admin, name='edit_business_admin'),
    path('super-admin/business/delete/<int:business_id>/', views.delete_business, name='delete_business'),
    path('super-admin/plans/', views.super_admin_plans, name='super_admin_plans'),
    path('super-admin/plans/add/', views.add_plan, name='add_plan'),
    path('super-admin/plans/edit/<int:plan_id>/', views.edit_plan, name='edit_plan'),
    path('super-admin/plans/delete/<int:plan_id>/', views.delete_plan, name='delete_plan'),
    path('super-admin/payment/approve/<int:payment_id>/', views.approve_upi_payment, name='approve_upi_payment'),
    path('super-admin/payment/reject/<int:payment_id>/', views.reject_upi_payment, name='reject_upi_payment'),
    path('super-admin/payment/delete/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    
    # Admin URLs
    path('store/cashiers/', views.manage_cashiers, name='manage_cashiers'),
    path('store/cashiers/add/', views.add_cashier, name='add_cashier'),
    path('subscription/purchase/', views.subscription_purchase, name='subscription_purchase'),
    path('subscription/checkout/<int:plan_id>/', views.subscription_checkout, name='subscription_checkout'),
    path('subscription/payment-callback/', views.payment_callback, name='payment_callback'),
    path('subscription/expired/', views.subscription_expired, name='subscription_expired'),
]

