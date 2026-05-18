from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
import json
import csv
from .models import Product, Supplier, Purchase, PurchaseItem
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from core.utils import filter_by_business, get_business

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def product_list(request):
    try:
        products = filter_by_business(Product.objects.all(), request)
    except Exception:
        # Dummy data
        products = [
            {'id': 1, 'sku': 'SKU001', 'name': 'Wireless Mouse', 'price': 25.00, 'stock_quantity': 4, 'min_stock_level': 5, 'is_low_stock': True},
            {'id': 2, 'sku': 'SKU002', 'name': 'Mechanical Keyboard', 'price': 120.00, 'stock_quantity': 15, 'min_stock_level': 5, 'is_low_stock': False},
            {'id': 3, 'sku': 'SKU003', 'name': 'USB-C Cable', 'price': 15.00, 'stock_quantity': 50, 'min_stock_level': 10, 'is_low_stock': False},
        ]
    return render(request, 'inventory/list.html', {'products': products})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def add_product(request):
    if request.method == 'POST':
        try:
            business = get_business(request)
            product = Product.objects.create(
                business=business,
                name=request.POST.get('name'),
                sku=request.POST.get('sku'),
                hsn_code=request.POST.get('hsn_code'),
                item_type=request.POST.get('item_type', 'PRODUCT'),
                price=request.POST.get('price'),
                stock_quantity=request.POST.get('stock', 0) if request.POST.get('item_type') == 'PRODUCT' else 0,
                gst_rate=request.POST.get('gst_rate', 18.0),
                image=request.FILES.get('image')
            )
            return JsonResponse({'status': 'success', 'id': product.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def add_purchase(request):
    if request.method == 'POST':
        try:
            business = get_business(request)
            supplier_id = request.POST.get('supplier_id')
            supplier = filter_by_business(Supplier.objects.all(), request).filter(id=supplier_id).first() if supplier_id else None
            
            product_id = request.POST.get('product_id')
            product = filter_by_business(Product.objects.all(), request).get(id=product_id)
            
            quantity = int(request.POST.get('quantity', 1))
            unit_cost = float(request.POST.get('unit_cost', 0.0))
            total = quantity * unit_cost
            
            purchase = Purchase.objects.create(
                business=business,
                supplier=supplier,
                payment_method=request.POST.get('payment_method', 'CASH'),
                invoice_number=request.POST.get('invoice_number'),
                total_amount=total
            )
            
            PurchaseItem.objects.create(
                purchase=purchase,
                product=product,
                quantity=quantity,
                unit_cost=unit_cost
            )
            
            return JsonResponse({'status': 'success', 'purchase_id': purchase.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def edit_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(filter_by_business(Product.objects.all(), request), id=product_id)
            product.name = request.POST.get('name')
            product.sku = request.POST.get('sku')
            product.hsn_code = request.POST.get('hsn_code')
            product.item_type = request.POST.get('item_type', 'PRODUCT')
            product.price = request.POST.get('price')
            if product.item_type == 'PRODUCT':
                product.stock_quantity = request.POST.get('stock', 0)
            else:
                product.stock_quantity = 0
            product.gst_rate = request.POST.get('gst_rate', 18.0)
            if request.FILES.get('image'):
                product.image = request.FILES.get('image')
            product.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(filter_by_business(Product.objects.all(), request), id=product_id)
            product.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def export_inventory(request):
    try:
        products = filter_by_business(Product.objects.all(), request).order_by('name')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Item Type', 'Item Name', 'Price (INR)', 'Stock Quantity', 'HSN/SAC Code', 'GST Rate (%)'])
        
        for p in products:
            writer.writerow([
                p.sku,
                p.get_item_type_display(),
                p.name,
                p.price,
                p.stock_quantity if p.item_type == 'PRODUCT' else 'N/A',
                p.hsn_code or '--',
                p.gst_rate
            ])
            
        return response
    except Exception as e:
        return HttpResponse(f"Error exporting inventory: {str(e)}", status=500)


