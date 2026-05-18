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
    
    # Admin URLs
    path('store/cashiers/', views.manage_cashiers, name='manage_cashiers'),
    path('store/cashiers/add/', views.add_cashier, name='add_cashier'),
]

