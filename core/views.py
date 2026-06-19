from django.shortcuts import render, redirect, get_object_or_404
from billing.models import Invoice, InvoiceItem
from inventory.models import Product, Supplier, Purchase
from django.db.models import Sum, F, Count
from django.db.models.functions import TruncMonth, TruncQuarter, TruncYear
from datetime import date
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from core.utils import filter_by_business, get_business
from core.models import Business, UserProfile, Plan, SubscriptionPayment
from billing.models import FestivalOffer
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta

@login_required(login_url='/accounts/login/')
def dashboard(request):
    # Redirect Super Admins to their specific command center
    if hasattr(request.user, 'profile') and request.user.profile.role == 'SUPER_ADMIN':
        return redirect('super_admin_dashboard')
        
    try:
        today = date.today()
        # Filter queries based on the user's shop/business
        todays_invoices = filter_by_business(Invoice.objects.filter(date__date=today), request)
        today_revenue = todays_invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
        total_sales = todays_invoices.count()
        low_stock_products = filter_by_business(Product.objects.all(), request).filter(stock_quantity__lte=F('min_stock_level')).count()
        
        # Monthly revenue breakdown
        rev_data = filter_by_business(Invoice.objects.all(), request).annotate(month=TruncMonth('date')).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')[:5]
        
        monthly_revenue_data = [float(item['total'] or 0) for item in rev_data]
        months = [item['month'].strftime('%b') if item['month'] else '' for item in rev_data]
        if not monthly_revenue_data:
             monthly_revenue_data = [0]
             months = ['N/A']
             
    except Exception as e:
        print("Dashboard error:", e)
        # Fallback to mock data if DB connection fails
        today_revenue = 24500.50
        total_sales = 42
        low_stock_products = 5
        monthly_revenue_data = [12000, 19000, 15000, 22000, 24500]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']

    business = get_business(request)
    now = timezone.now()
    
    if business:
        active_offers = FestivalOffer.objects.filter(
            business=business,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-priority')
        festival_mode = business.festival_offer_enabled
    else:
        active_offers = FestivalOffer.objects.none()
        festival_mode = False

    days_remaining = None
    show_expiry_warning = False
    if business and business.subscription_plan and business.subscription_end_date:
        days_remaining = (business.subscription_end_date.date() - timezone.now().date()).days
        if 0 <= days_remaining <= 5:
            show_expiry_warning = True

    context = {
        'today_revenue': today_revenue,
        'total_sales': total_sales,
        'low_stock_count': low_stock_products,
        'monthly_revenue_data': monthly_revenue_data,
        'months': months,
        'active_offers': active_offers,
        'festival_mode': festival_mode,
        'business': business,
        'show_expiry_warning': show_expiry_warning,
        'days_remaining': days_remaining
    }
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def reports(request):
    try:
        invoices = filter_by_business(Invoice.objects.all(), request).order_by('-date')[:50]
        purchases = filter_by_business(Purchase.objects.all(), request).order_by('-purchase_date')[:50]
        suppliers = filter_by_business(Supplier.objects.all(), request).order_by('name')
        products = filter_by_business(Product.objects.filter(item_type='PRODUCT'), request).order_by('name')
        
        total_sales = filter_by_business(Invoice.objects.all(), request).aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
        total_purchases = filter_by_business(Purchase.objects.all(), request).aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
        balance = float(total_sales) - float(total_purchases)
        
        # GST Aggregation
        total_gst = filter_by_business(Invoice.objects.all(), request).aggregate(Sum('gst_amount'))['gst_amount__sum'] or 0.00
        total_cgst = filter_by_business(Invoice.objects.all(), request).aggregate(Sum('cgst_amount'))['cgst_amount__sum'] or 0.00
        total_sgst = filter_by_business(Invoice.objects.all(), request).aggregate(Sum('sgst_amount'))['sgst_amount__sum'] or 0.00
        taxable_value = float(total_sales) - float(total_gst)
        
        # Dynamic GST Slabs Breakdown
        slab_data = filter_by_business(InvoiceItem.objects.all(), request).values('gst_rate').annotate(
            total_val=Sum('total_price')
        ).order_by('gst_rate')
        
        gst_slabs = []
        for entry in slab_data:
            rate = float(entry['gst_rate'])
            gross = float(entry['total_val'])
            # Calculate components from inclusive amount!
            tax = gross * (rate / (100 + rate)) if rate > 0 else 0.0
            taxable = gross - tax
            gst_slabs.append({
                'rate': entry['gst_rate'],
                'taxable': round(taxable, 2),
                'cgst': round(tax / 2, 2),
                'sgst': round(tax / 2, 2),
                'total_tax': round(tax, 2),
                'gross': round(gross, 2)
            })
            
    except Exception as e:
        print("Reports computation error:", e)
        invoices = []
        purchases = []
        suppliers = []
        products = []
        total_sales = 0.00
        total_purchases = 0.00
        balance = 0.00
        total_gst = 0.00
        total_cgst = 0.00
        total_sgst = 0.00
        taxable_value = 0.00
        gst_slabs = []
    
    context = {
        'invoices': invoices,
        'purchases': purchases,
        'suppliers': suppliers,
        'products': products,
        'total_sales': round(total_sales, 2),
        'total_purchases': round(total_purchases, 2),
        'balance': round(balance, 2),
        
        # Add GST context variables
        'total_gst': round(total_gst, 2),
        'total_cgst': round(total_cgst, 2),
        'total_sgst': round(total_sgst, 2),
        'taxable_value': round(taxable_value, 2),
        'gst_slabs': gst_slabs
    }
    return render(request, 'core/reports.html', context)

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def reports_summary(request):
    try:
        # Monthly aggregates
        monthly = filter_by_business(Invoice.objects.all(), request).annotate(period=TruncMonth('date')).values('period').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-period')
        
        # Quarterly aggregates
        quarterly = filter_by_business(Invoice.objects.all(), request).annotate(period=TruncQuarter('date')).values('period').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-period')
        
        # Yearly aggregates
        yearly = filter_by_business(Invoice.objects.all(), request).annotate(period=TruncYear('date')).values('period').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-period')
    except Exception as e:
        print("Analytics Error:", e)
        monthly = []
        quarterly = []
        yearly = []

    context = {
        'monthly': monthly,
        'quarterly': quarterly,
        'yearly': yearly
    }
    return render(request, 'core/summary.html', context)

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def reports_tax_profit(request):
    try:
        # Aggregate Sales & Tax by Month
        sales_data = filter_by_business(Invoice.objects.all(), request).annotate(month=TruncMonth('date')).values('month').annotate(
            total_sales=Sum('total_amount'),
            total_tax=Sum('gst_amount')
        ).order_by('-month')

        # Aggregate Purchases by Month
        purchase_data = filter_by_business(Purchase.objects.all(), request).annotate(month=TruncMonth('purchase_date')).values('month').annotate(
            total_cost=Sum('total_amount')
        ).order_by('-month')

        # Master merge table keyed by period
        periods = {}
        for item in sales_data:
            key = item['month']
            if key:
                periods[key] = {
                    'sales': float(item['total_sales'] or 0.0),
                    'tax': float(item['total_tax'] or 0.0),
                    'purchases': 0.0
                }

        for item in purchase_data:
            key = item['month']
            if key:
                if key not in periods:
                    periods[key] = {'sales': 0.0, 'tax': 0.0, 'purchases': 0.0}
                periods[key]['purchases'] = float(item['total_cost'] or 0.0)

        # Consolidate and compute financial vectors
        report_list = []
        overall_sales = 0.0
        overall_tax = 0.0
        overall_purchases = 0.0

        for key in sorted(periods.keys(), reverse=True):
            val = periods[key]
            sales = val['sales']
            tax = val['tax']
            purchases = val['purchases']
            
            profit = sales - purchases
            margin = (profit / sales * 100) if sales > 0 else 0.0
            
            report_list.append({
                'period': key,
                'sales': round(sales, 2),
                'tax': round(tax, 2),
                'purchases': round(purchases, 2),
                'profit': round(profit, 2),
                'margin': round(margin, 2)
            })
            
            overall_sales += sales
            overall_tax += tax
            overall_purchases += purchases
            
        overall_profit = overall_sales - overall_purchases
        
    except Exception as e:
        print("Tax Profit Reporter Error:", e)
        report_list = []
        overall_sales = 0.0
        overall_tax = 0.0
        overall_purchases = 0.0
        overall_profit = 0.0

    context = {
        'report_list': report_list,
        'overall_sales': round(overall_sales, 2),
        'overall_tax': round(overall_tax, 2),
        'overall_purchases': round(overall_purchases, 2),
        'overall_profit': round(overall_profit, 2)
    }
    return render(request, 'core/tax_profit.html', context)

def homepage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

# === SUPER ADMIN VIEWS ===

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def super_admin_dashboard(request):
    businesses = Business.objects.all().annotate(
        total_invoices=Count('invoices', distinct=True),
        total_revenue=Sum('invoices__total_amount')
    )
    total_businesses = Business.objects.count()
    active_subs = Business.objects.filter(is_subscription_active=True).count()
    total_rev_agg = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
    plans = Plan.objects.all()
    
    # Calculate Super Admin's Subscription Earnings
    sub_rev_agg = SubscriptionPayment.objects.filter(status='SUCCESS').aggregate(Sum('amount'))['amount__sum'] or 0.00
    
    # Fetch recent payments
    recent_payments = SubscriptionPayment.objects.all().order_by('-created_at')[:10]
    
    # Calculate notifications (successful payments in the last 24 hours)
    one_day_ago = timezone.now() - timedelta(hours=24)
    recent_notifications = SubscriptionPayment.objects.filter(status='SUCCESS', updated_at__gte=one_day_ago).order_by('-updated_at')
    
    context = {
        'businesses': businesses,
        'total_businesses': total_businesses,
        'active_subs': active_subs,
        'total_revenue': round(total_rev_agg, 2),
        'subscription_revenue': round(sub_rev_agg, 2),
        'recent_payments': recent_payments,
        'recent_notifications': recent_notifications,
        'plans': plans
    }
    return render(request, 'core/super_admin_dashboard.html', context)


@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def toggle_subscription(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    business.is_subscription_active = not business.is_subscription_active
    business.save()
    messages.success(request, f"Subscription status updated for '{business.name}'!")
    return redirect('super_admin_dashboard')

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def add_business_admin(request):
    if request.method == 'POST':
        b_name = request.POST.get('business_name')
        owner_name = request.POST.get('owner_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        gstin = request.POST.get('gstin')
        address = request.POST.get('address')
        logo = request.FILES.get('logo')
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('super_admin_dashboard')
            
        business = Business.objects.create(
            name=b_name, owner_name=owner_name, phone=phone, email=email, gstin=gstin, address=address, logo=logo,
            subscription_plan=None,
            is_subscription_active=True,
            subscription_end_date=timezone.now() - timedelta(days=1)
        )
        
        user = User.objects.create_user(username=username, password=password, email=email)
        
        profile = user.profile
        profile.role = 'ADMIN'
        profile.business = business
        profile.save()
        
        messages.success(request, f"Successfully created business '{b_name}' and set up Admin '{username}'!")
    return redirect('super_admin_dashboard')

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def edit_business_admin(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    if request.method == 'POST':
        try:
            business.name = request.POST.get('business_name')
            business.owner_name = request.POST.get('owner_name')
            business.phone = request.POST.get('phone')
            business.email = request.POST.get('email')
            business.gstin = request.POST.get('gstin')
            business.address = request.POST.get('address')
            
            logo = request.FILES.get('logo')
            if logo:
                business.logo = logo
                
            business.save()
            messages.success(request, f"Business details updated successfully for '{business.name}'!")
        except Exception as e:
            messages.error(request, f"Error updating business: {str(e)}")
            
    return redirect('super_admin_dashboard')
            
    return redirect('super_admin_dashboard')

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def delete_business(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    name = business.name
    try:
        # Delete invoices and their items first to avoid models.PROTECT violations on InvoiceItem.product
        Invoice.objects.filter(business=business).delete()
        
        # Delete associated Django User objects first
        users_to_delete = User.objects.filter(profile__business=business)
        users_to_delete.delete()
        
        # Cascade delete the Business object
        business.delete()
        
        messages.success(request, f"Business '{name}' and all its associated staff, inventory, and invoice data have been successfully deleted.")
    except Exception as e:
        messages.error(request, f"Error deleting business '{name}': {str(e)}")
        
    return redirect('super_admin_dashboard')

# === SHOP ADMIN CASHIER MANAGEMENT ===

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def manage_cashiers(request):
    business = get_business(request)
    cashiers = UserProfile.objects.filter(business=business, role='CASHIER')
    return render(request, 'core/manage_cashiers.html', {
        'cashiers': cashiers,
        'business': business
    })

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def add_cashier(request):
    business = get_business(request)
    if business and business.subscription_plan:
        max_c = business.subscription_plan.max_cashiers
        if max_c != -1:
            current_c = UserProfile.objects.filter(business=business, role='CASHIER').count()
            if current_c >= max_c:
                messages.error(request, f"Cashier limit reached! Your current plan allows a maximum of {max_c} cashier accounts. Please upgrade your plan to add more.")
                return redirect('manage_cashiers')
                
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "A user with that username already exists!")
            return render(request, 'core/add_cashier.html', {'business': business, 'error': 'Username already taken.'})
            
        user = User.objects.create_user(username=username, password=password, email=email)
        
        profile = user.profile
        profile.role = 'CASHIER'
        profile.business = business
        profile.save()
        
        messages.success(request, f"Cashier account '{username}' added successfully!")
        return redirect('manage_cashiers')
        
    return render(request, 'core/add_cashier.html', {'business': business})


# === PLAN MANAGEMENT (SUPER ADMIN CRUD) ===

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def super_admin_plans(request):
    plans = Plan.objects.all().order_by('price_3_months')
    return render(request, 'core/super_admin_plans.html', {'plans': plans})

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def add_plan(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price_3_months = request.POST.get('price_3_months', '0.00')
        price_6_months = request.POST.get('price_6_months', '0.00')
        price_year = request.POST.get('price_year', '0.00')
        max_cashiers = request.POST.get('max_cashiers')
        description = request.POST.get('description')
        
        has_festival_offers = request.POST.get('has_festival_offers') == 'on'
        has_batch_tracking = request.POST.get('has_batch_tracking') == 'on'
        has_smart_insights = request.POST.get('has_smart_insights') == 'on'
        has_forecasting = request.POST.get('has_forecasting') == 'on'
        has_dynamic_pricing = request.POST.get('has_dynamic_pricing') == 'on'
        has_advanced_reports = request.POST.get('has_advanced_reports') == 'on'
        
        Plan.objects.create(
            name=name, price_3_months=price_3_months, price_6_months=price_6_months, price_year=price_year,
            max_cashiers=max_cashiers, description=description,
            has_festival_offers=has_festival_offers, has_batch_tracking=has_batch_tracking,
            has_smart_insights=has_smart_insights, has_forecasting=has_forecasting,
            has_dynamic_pricing=has_dynamic_pricing, has_advanced_reports=has_advanced_reports
        )
        messages.success(request, f"Plan '{name}' created successfully!")
        return redirect('super_admin_plans')
        
    return render(request, 'core/plan_form.html', {'title': 'Add Plan'})

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def edit_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.price_3_months = request.POST.get('price_3_months', '0.00')
        plan.price_6_months = request.POST.get('price_6_months', '0.00')
        plan.price_year = request.POST.get('price_year', '0.00')
        plan.max_cashiers = request.POST.get('max_cashiers')
        plan.description = request.POST.get('description')
        
        plan.has_festival_offers = request.POST.get('has_festival_offers') == 'on'
        plan.has_batch_tracking = request.POST.get('has_batch_tracking') == 'on'
        plan.has_smart_insights = request.POST.get('has_smart_insights') == 'on'
        plan.has_forecasting = request.POST.get('has_forecasting') == 'on'
        plan.has_dynamic_pricing = request.POST.get('has_dynamic_pricing') == 'on'
        plan.has_advanced_reports = request.POST.get('has_advanced_reports') == 'on'
        
        plan.save()
        messages.success(request, f"Plan '{plan.name}' updated successfully!")
        return redirect('super_admin_plans')
        
    return render(request, 'core/plan_form.html', {'plan': plan, 'title': 'Edit Plan'})

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    if plan.businesses.exists():
        messages.error(request, f"Cannot delete plan '{plan.name}' because it has active subscriptions associated with it.")
    else:
        plan.delete()
        messages.success(request, f"Plan deleted successfully.")
    return redirect('super_admin_plans')


# === SUBSCRIPTIONS AND RAZORPAY ===

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def subscription_purchase(request):
    business = get_business(request)
    plans = Plan.objects.all().order_by('price_3_months')
    return render(request, 'core/subscription_purchase.html', {
        'business': business,
        'plans': plans
    })

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def subscription_checkout(request, plan_id):
    business = get_business(request)
    plan = get_object_or_404(Plan, id=plan_id)
    
    # Get chosen duration: 3, 6, or 12 months
    duration = int(request.GET.get('duration', 3))
    if duration == 6:
        price = plan.price_6_months
        duration_months = 6
    elif duration == 12:
        price = plan.price_year
        duration_months = 12
    else:
        price = plan.price_3_months
        duration_months = 3
        
    import random
    import string
    # Generate unique local order reference ID
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    order_id = f"UPI-ORD-{random_suffix}"
    
    # Get UPI ID from settings
    upi_id = getattr(settings, 'UPI_ID', 'billing@zenelait')
    
    # Construct standard UPI Payment URI
    # upi://pay?pa=merchant@upi&pn=Name&am=100&tr=Order123&cu=INR&tn=Notes
    import urllib.parse
    clean_biz_name = urllib.parse.quote(business.name)
    clean_plan_name = urllib.parse.quote(plan.name)
    upi_uri = f"upi://pay?pa={upi_id}&pn={clean_biz_name}&am={price}&tr={order_id}&cu=INR&tn=Zenelait%20-{clean_plan_name}"
    
    # Save payment history in PENDING state
    SubscriptionPayment.objects.create(
        business=business,
        plan=plan,
        razorpay_order_id=order_id, # Reusing this field as the unique order code
        amount=price,
        duration_months=duration_months,
        status='PENDING'
    )
    
    context = {
        'business': business,
        'plan': plan,
        'order_id': order_id,
        'duration_months': duration_months,
        'price': price,
        'upi_id': upi_id,
        'upi_uri': upi_uri
    }
    return render(request, 'core/subscription_checkout.html', context)

@login_required(login_url='/accounts/login/')
def payment_callback(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        utr_number = request.POST.get('upi_utr_number')
        
        if not utr_number or len(utr_number.strip()) < 6:
            messages.error(request, "Please enter a valid UPI Transaction ID / UTR number.")
            return redirect(request.META.get('HTTP_REFERER', 'subscription_purchase'))
            
        payment = get_object_or_404(SubscriptionPayment, razorpay_order_id=order_id)
        payment.upi_utr_number = utr_number.strip()
        payment.save()
        
        messages.success(request, f"Your payment details (UTR: {utr_number}) have been successfully submitted for verification. Your subscription will be activated once the administrator confirms receipt!")
        return redirect('dashboard')
            
    return redirect('dashboard')

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def approve_upi_payment(request, payment_id):
    payment = get_object_or_404(SubscriptionPayment, id=payment_id)
    if payment.status == 'PENDING':
        payment.status = 'SUCCESS'
        payment.save()
        
        # Update business plan
        business = payment.business
        business.subscription_plan = payment.plan
        business.is_subscription_active = True
        
        # Extend subscription end date
        days_to_add = payment.duration_months * 30
        now = timezone.now()
        if business.subscription_end_date and business.subscription_end_date > now:
            business.subscription_end_date += timedelta(days=days_to_add)
        else:
            business.subscription_end_date = now + timedelta(days=days_to_add)
        business.save()
        
        messages.success(request, f"Approved payment for business '{business.name}'. Plan '{payment.plan.name}' activated/extended until {business.subscription_end_date.strftime('%Y-%m-%d')}!")
    else:
        messages.warning(request, "This payment has already been processed.")
    return redirect('super_admin_dashboard')

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def reject_upi_payment(request, payment_id):
    payment = get_object_or_404(SubscriptionPayment, id=payment_id)
    if payment.status == 'PENDING':
        payment.status = 'FAILED'
        payment.save()
        messages.error(request, f"Payment rejected for business '{payment.business.name}'.")
    else:
        messages.warning(request, "This payment has already been processed.")
    return redirect('super_admin_dashboard')

@login_required(login_url='/accounts/login/')
@role_required(['SUPER_ADMIN'])
def delete_payment(request, payment_id):
    payment = get_object_or_404(SubscriptionPayment, id=payment_id)
    ref = payment.razorpay_order_id
    payment.delete()
    messages.success(request, f"Payment record {ref} deleted successfully.")
    return redirect('super_admin_dashboard')

@login_required(login_url='/accounts/login/')
def subscription_expired(request):
    business = get_business(request)
    is_admin = hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'
    return render(request, 'core/subscription_expired.html', {
        'business': business,
        'is_admin': is_admin
    })


