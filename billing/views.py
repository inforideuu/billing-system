from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
from inventory.models import Product, Category
from .models import Customer, Invoice, InvoiceItem
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from core.utils import filter_by_business, get_business
from core.decorators import role_required, plan_feature_required
from .models import Customer, Invoice, InvoiceItem, FestivalOffer
from django.contrib import messages
from django.shortcuts import redirect

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def pos(request):
    # Fetch all products to display in the POS catalog
    try:
        business = get_business(request)
        products = filter_by_business(Product.objects.all(), request)
        from intelligence.utils import get_dynamic_price
        for product in products:
            if product.item_type == 'PRODUCT':
                dyn_price, is_active, reason = get_dynamic_price(product, business)
                product.original_price = float(product.price)
                product.dynamic_price = dyn_price
                product.is_dynamic_active = is_active
                product.dynamic_reason = reason
            else:
                product.original_price = float(product.price)
                product.dynamic_price = float(product.price)
                product.is_dynamic_active = False
                product.dynamic_reason = "Base Price"
    except Exception:
        # Fallback dummy data if DB not ready
        products = [
            {'id': 1, 'name': 'Wireless Mouse', 'price': 25.00, 'gst_rate': 18.00, 'is_dynamic_active': False, 'original_price': 25.00, 'dynamic_price': 25.00, 'dynamic_reason': 'Base'},
            {'id': 2, 'name': 'Mechanical Keyboard', 'price': 120.00, 'gst_rate': 18.00, 'is_dynamic_active': False, 'original_price': 120.00, 'dynamic_price': 120.00, 'dynamic_reason': 'Base'},
            {'id': 3, 'name': 'USB-C Cable', 'price': 15.00, 'gst_rate': 5.00, 'is_dynamic_active': False, 'original_price': 15.00, 'dynamic_price': 15.00, 'dynamic_reason': 'Base'},
            {'id': 4, 'name': 'HD Monitor', 'price': 300.00, 'gst_rate': 28.00, 'is_dynamic_active': False, 'original_price': 300.00, 'dynamic_price': 300.00, 'dynamic_reason': 'Base'},
        ]
        
    context = {
        'products': products,
        'offers': get_active_offers_data(request)
    }
    return render(request, 'billing/pos.html', context)

def get_active_offers_data(request):
    business = get_business(request)
    if not business or not business.festival_offer_enabled:
        return []
    
    now = timezone.now()
    offers = FestivalOffer.objects.filter(
        business=business,
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).order_by('-priority', '-discount_value')
    
    offer_list = []
    for offer in offers:
        offer_list.append({
            'id': offer.id,
            'name': offer.name,
            'discount_type': offer.discount_type,
            'discount_value': float(offer.discount_value),
            'apply_to_all': offer.apply_to_all,
            'product_ids': list(offer.products.values_list('id', flat=True)),
            'category_ids': list(offer.categories.values_list('id', flat=True))
        })
    return offer_list

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def customer_list(request):
    try:
        customers = filter_by_business(Customer.objects.all(), request)
    except Exception:
        customers = []
    return render(request, 'billing/customers.html', {'customers': customers})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def process_payment(request):
    if request.method == 'POST':
        try:
            business = get_business(request)
            data = json.loads(request.body)
            
            # 1. Get or Create Customer within the business scope
            customer_name = data.get('customerName', '').strip()
            customer_phone = data.get('customerPhone', '').strip()
            customer_email = data.get('customerEmail', '').strip()
            customer_gstin = data.get('customerGstin', '').strip()
            if not customer_name:
                customer_name = 'Walk-in Customer'
            
            customer_qs = filter_by_business(Customer.objects.all(), request).filter(name=customer_name)
            if customer_qs.exists():
                customer = customer_qs.first()
            else:
                customer = Customer.objects.create(business=business, name=customer_name)
            
            if customer_phone:
                customer.phone = customer_phone
            if customer_email:
                customer.email = customer_email
            if customer_gstin:
                customer.gstin = customer_gstin
            customer.save()
            
            # 2. Create Invoice
            gst_total = float(data.get('gstTotal', 0))
            cgst = gst_total / 2.0
            sgst = gst_total / 2.0
            
            # Recalculate or trust frontend? For safety, we should recalculate discounts here if needed.
            # But since the user wants it automatic and we might have complex rules, 
            # let's capture the offer name if provided or determine it.
            
            applied_offer_name = data.get('appliedOfferName', '')
            discount_total = float(data.get('discountTotal', 0))

            invoice = Invoice.objects.create(
                business=business,
                user=request.user,
                customer=customer,
                total_amount=data['grandTotal'],
                discount_amount=discount_total,
                applied_offer_name=applied_offer_name,
                gst_amount=gst_total,
                cgst_amount=cgst,
                sgst_amount=sgst,
                payment_method=data['paymentMethod'],
                status='PAID'
            )
            
            # 3. Create Invoice Items and Update Stock
            for item in data['cart']:
                product = get_object_or_404(filter_by_business(Product.objects.all(), request), id=item['id'])
                
                # Create Item
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=item['qty'],
                    original_unit_price=item['price'], # This is original price before discount
                    discount_amount=item.get('discount', 0),
                    unit_price=item['finalPrice'], # This is discounted price
                    hsn_code=product.hsn_code,
                    gst_rate=product.gst_rate,
                    total_price=float(item['finalPrice']) * int(item['qty'])
                )
                
                # Decrement Stock if Physical Product
                if product.item_type == 'PRODUCT':
                    from datetime import date
                    product_batches = product.batches.filter(expiry_date__gt=date.today(), stock_quantity__gt=0).order_by('expiry_date')
                    
                    if product.batches.exists():
                        total_unexpired_stock = sum(b.stock_quantity for b in product_batches)
                        if total_unexpired_stock < int(item['qty']):
                            raise Exception(f"Cannot sell product '{product.name}': Insufficient unexpired batch stock. Available: {total_unexpired_stock}")
                        
                        qty_left = int(item['qty'])
                        for b in product_batches:
                            if qty_left <= 0:
                                break
                            if b.stock_quantity >= qty_left:
                                b.stock_quantity -= qty_left
                                b.save()
                                qty_left = 0
                            else:
                                qty_left -= b.stock_quantity
                                b.stock_quantity = 0
                                b.save()
                                
                    product.stock_quantity -= int(item['qty'])
                    product.save()
                
            return JsonResponse({'status': 'success', 'invoice_id': invoice.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def view_invoice(request, pk):
    invoice = get_object_or_404(filter_by_business(Invoice.objects.all(), request), pk=pk)
    
    # Subtotal = total invoice amount - total gst
    subtotal = float(invoice.total_amount) - float(invoice.gst_amount)
    
    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
        'subtotal': round(subtotal, 2)
    }
    return render(request, 'billing/invoice.html', context)

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
@plan_feature_required('has_festival_offers')
def manage_festival_offers(request):
    business = get_business(request)
    if request.method == 'POST':
        # Handle global toggle
        business.festival_offer_enabled = request.POST.get('festival_mode') == 'on'
        business.save()
        messages.success(request, f"Festival Offer Mode {'enabled' if business.festival_offer_enabled else 'disabled'} successfully.")
        return redirect('manage_festival_offers')

    offers = FestivalOffer.objects.filter(business=business).order_by('-priority', '-start_date')
    return render(request, 'billing/festival_offers.html', {
        'offers': offers,
        'business': business
    })

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
@plan_feature_required('has_festival_offers')
def add_festival_offer(request):
    business = get_business(request)
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            discount_type = request.POST.get('discount_type')
            discount_value = request.POST.get('discount_value')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            priority = request.POST.get('priority', 0)
            apply_to_all = request.POST.get('apply_to_all') == 'on'
            
            offer = FestivalOffer.objects.create(
                business=business,
                name=name,
                discount_type=discount_type,
                discount_value=discount_value,
                start_date=start_date,
                end_date=end_date,
                priority=priority,
                apply_to_all=apply_to_all
            )
            
            if not apply_to_all:
                product_ids = request.POST.getlist('products')
                category_ids = request.POST.getlist('categories')
                if product_ids:
                    offer.products.set(product_ids)
                if category_ids:
                    offer.categories.set(category_ids)
            
            messages.success(request, f"Offer '{name}' created successfully!")
            return redirect('manage_festival_offers')
        except Exception as e:
            messages.error(request, f"Error creating offer: {e}")

    products = filter_by_business(Product.objects.all(), request)
    categories = filter_by_business(Category.objects.all(), request)
    return render(request, 'billing/festival_offer_form.html', {
        'products': products,
        'categories': categories,
        'title': 'Add New Festival Offer'
    })

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
@plan_feature_required('has_festival_offers')
def delete_festival_offer(request, pk):
    offer = get_object_or_404(FestivalOffer, pk=pk, business=get_business(request))
    name = offer.name
    offer.delete()
    messages.success(request, f"Offer '{name}' deleted successfully.")
    return redirect('manage_festival_offers')

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def add_customer(request):
    if request.method == 'POST':
        try:
            business = get_business(request)
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip()
            gstin = request.POST.get('gstin', '').strip()
            
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Name is required'})
                
            customer = Customer.objects.create(
                business=business,
                name=name,
                phone=phone,
                email=email,
                gstin=gstin
            )
            return JsonResponse({'status': 'success', 'id': customer.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def edit_customer(request, pk):
    customer = get_object_or_404(filter_by_business(Customer.objects.all(), request), pk=pk)
    if request.method == 'POST':
        try:
            customer.name = request.POST.get('name', '').strip()
            customer.phone = request.POST.get('phone', '').strip()
            customer.email = request.POST.get('email', '').strip()
            customer.gstin = request.POST.get('gstin', '').strip()
            customer.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({
        'id': customer.id,
        'name': customer.name,
        'phone': customer.phone or '',
        'email': customer.email or '',
        'gstin': customer.gstin or ''
    })

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def delete_customer(request, pk):
    if request.method == 'POST':
        try:
            customer = get_object_or_404(filter_by_business(Customer.objects.all(), request), pk=pk)
            customer.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN', 'CASHIER'])
def send_invoice_email(request, pk):
    if request.method == 'POST':
        try:
            invoice = get_object_or_404(filter_by_business(Invoice.objects.all(), request), pk=pk)
            recipient_email = request.POST.get('email', '').strip()
            
            if not recipient_email:
                return JsonResponse({'status': 'error', 'message': 'Recipient email address is required'})
            
            subtotal = float(invoice.total_amount) - float(invoice.gst_amount)
            
            # Context context
            context = {
                'invoice': invoice,
                'items': invoice.items.all(),
                'subtotal': round(subtotal, 2),
                'domain': request.build_absolute_uri('/')[:-1] # Build root URL for logo/links
            }
            
            # Render email templates
            html_content = render_to_string('billing/email_invoice.html', context)
            text_content = strip_tags(html_content)
            
            # Dispatch email
            subject = f"Tax Invoice #{invoice.id} | RetailPos"
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'billing@retailpos.com')
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, [recipient_email])
            msg.attach_alternative(html_content, "text/html")
            
            # Check for attached invoice image from frontend and attach
            if 'invoice_image' in request.FILES:
                invoice_img = request.FILES['invoice_image']
                msg.attach(invoice_img.name, invoice_img.read(), 'image/png')
                
            msg.send()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

