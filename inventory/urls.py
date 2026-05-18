from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='inventory_list'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('purchase/add/', views.add_purchase, name='add_purchase'),
    path('export/', views.export_inventory, name='export_inventory'),
]
