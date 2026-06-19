import os
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, F, Count
from django.core.mail import send_mail
from django.conf import settings
from inventory.models import Product, Batch
from billing.models import Invoice, InvoiceItem

def get_average_daily_sales(product, days=30):
    """
    Calculate average daily sales of a product over the last X days.
    """
    if product.item_type != 'PRODUCT':
        return 0.0
        
    cutoff_date = timezone.now() - timedelta(days=days)
    total_sold = InvoiceItem.objects.filter(
        product=product,
        invoice__date__gte=cutoff_date,
        invoice__status='PAID'
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    return float(total_sold) / float(days)

def predict_stock_out_days(product, avg_daily_sales=None):
    """
    Predict number of days before a product runs out of stock.
    """
    if product.item_type != 'PRODUCT' or product.stock_quantity <= 0:
        return 0
        
    if avg_daily_sales is None:
        avg_daily_sales = get_average_daily_sales(product)
        
    if avg_daily_sales <= 0:
        return 9999  # Safe fallback representing infinite days (won't run out soon)
        
    return int(product.stock_quantity / avg_daily_sales)

def get_dynamic_price(product, business):
    """
    Calculate the dynamic price of a product based on stock, demand, and batch expiry rules.
    Priority: Near-expiry Clearance Discount -> Low Stock Markup -> High Demand Markup.
    """
    if not business or not business.dynamic_pricing_enabled or product.item_type != 'PRODUCT':
        return float(product.price), False, "Base Price"
        
    base_price = float(product.price)
    today = date.today()
    
    # 1. Near-expiry Clearance Rule (Discount)
    if business.batch_tracking_enabled:
        soon_expiring_batch = Batch.objects.filter(
            business=business,
            product=product,
            stock_quantity__gt=0,
            expiry_date__gt=today,
            expiry_date__lte=today + timedelta(days=business.expiry_alert_days)
        ).order_by('expiry_date').first()
        
        if soon_expiring_batch:
            discount = (float(business.pricing_clearance_percent) / 100.0) * base_price
            clearance_price = max(0.01, base_price - discount)
            days_left = (soon_expiring_batch.expiry_date - today).days
            return round(clearance_price, 2), True, f"Clearance Discount ({int(business.pricing_clearance_percent)}% off) - Batch expiring in {days_left} days"
        
    # 2. Low Stock Rule (Markup)
    if product.stock_quantity <= business.low_stock_threshold:
        markup = (float(business.pricing_low_stock_percent) / 100.0) * base_price
        low_stock_price = base_price + markup
        return round(low_stock_price, 2), True, f"Low Stock Markup (+{int(business.pricing_low_stock_percent)}%)"
        
    # 3. High Demand Rule (Markup)
    # Check if sales in last 7 days average is high (e.g. > 1.5 units per day)
    recent_avg_sales = get_average_daily_sales(product, days=7)
    if recent_avg_sales > 1.5:
        markup = (float(business.pricing_high_demand_percent) / 100.0) * base_price
        high_demand_price = base_price + markup
        return round(high_demand_price, 2), True, f"High Demand Markup (+{int(business.pricing_high_demand_percent)}%)"
        
    return base_price, False, "Base Price"

def get_smart_insights(request, business):
    """
    Compile comprehensive alerts, stats, and trends for the Smart Insights dashboard.
    """
    insights = {
        'alerts': [],
        'sales_performance': {},
        'top_sellers': [],
        'slow_movers': [],
        'dead_stock': []
    }
    
    if not business or not business.smart_insights_enabled:
        return insights
        
    from .models import DismissedAlert
    dismissed_keys = set(DismissedAlert.objects.filter(business=business).values_list('alert_key', flat=True))
    
    def add_alert(alert_type, title, message, key, badge_color, product_id=None):
        if key not in dismissed_keys:
            alert_dict = {
                'type': alert_type,
                'title': title,
                'message': message,
                'key': key,
                'badge_color': badge_color
            }
            if product_id:
                alert_dict['product_id'] = product_id
            insights['alerts'].append(alert_dict)
            
    today = date.today()
    products = Product.objects.filter(business=business, item_type='PRODUCT')
    
    # 1. Product run-out predictions
    for p in products:
        avg_sales = get_average_daily_sales(p)
        if avg_sales > 0:
            days_left = predict_stock_out_days(p, avg_sales)
            if days_left <= 7:
                add_alert(
                    'RUN_OUT_CRITICAL' if days_left <= 3 else 'RUN_OUT_WARNING',
                    'Stock depletion alert',
                    f"Product '{p.name}' will run out in approximately {days_left} days based on sales velocity.",
                    f"run_out_{p.id}_{days_left}",
                    'bg-rose-100 text-rose-700' if days_left <= 3 else 'bg-amber-100 text-amber-700',
                    p.id
                )
        elif p.stock_quantity <= business.low_stock_threshold:
            add_alert(
                'LOW_STOCK',
                'Low stock warning',
                f"Product '{p.name}' is below low stock threshold. Current stock: {p.stock_quantity}.",
                f"low_stock_{p.id}",
                'bg-amber-100 text-amber-700',
                p.id
            )
            
    # 2. Expiry warnings
    if business.batch_tracking_enabled:
        batches = Batch.objects.filter(business=business, stock_quantity__gt=0)
        for b in batches:
            if b.expiry_date <= today:
                add_alert(
                    'EXPIRED',
                    'Expired inventory',
                    f"Batch '{b.batch_number}' of '{b.product.name}' expired on {b.expiry_date}!",
                    f"expired_{b.id}",
                    'bg-rose-200 text-rose-800 font-bold',
                    b.product.id
                )
            elif b.expiry_date <= today + timedelta(days=business.expiry_alert_days):
                days_left = (b.expiry_date - today).days
                add_alert(
                    'EXPIRING_SOON',
                    'Expiry warning',
                    f"Batch '{b.batch_number}' of '{b.product.name}' expires in {days_left} days ({b.expiry_date}).",
                    f"expiring_{b.id}",
                    'bg-amber-100 text-amber-700',
                    b.product.id
                )
            
    # 3. Monthly Sales Trajectory comparison
    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Last month
    last_month_end = this_month_start - timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    this_month_sales = Invoice.objects.filter(
        business=business,
        date__gte=this_month_start,
        status='PAID'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
    
    last_month_sales = Invoice.objects.filter(
        business=business,
        date__gte=last_month_start,
        date__lte=last_month_end,
        status='PAID'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
    
    this_month_sales = float(this_month_sales)
    last_month_sales = float(last_month_sales)
    
    if last_month_sales > 0:
        change_pct = ((this_month_sales - last_month_sales) / last_month_sales) * 100.0
        insights['sales_performance'] = {
            'this_month': this_month_sales,
            'last_month': last_month_sales,
            'change_percent': round(change_pct, 2),
            'change_percent_abs': abs(round(change_pct, 2)),
            'trend': 'UP' if change_pct >= 0 else 'DOWN'
        }
        if change_pct < -5.0:
            add_alert(
                'SALES_DROP',
                'Sales performance warning',
                f"Sales dropped by {abs(round(change_pct, 1))}% compared to last month.",
                f"sales_drop_{this_month_start.strftime('%Y_%m')}",
                'bg-rose-100 text-rose-700'
            )
    else:
        insights['sales_performance'] = {
            'this_month': this_month_sales,
            'last_month': 0.0,
            'change_percent': 0.0,
            'trend': 'STABLE'
        }
        
    # 4. Top sellers & slow movers (past 30 days)
    cutoff_30 = now - timedelta(days=30)
    sales_past_30 = InvoiceItem.objects.filter(
        product__business=business,
        invoice__date__gte=cutoff_30,
        invoice__status='PAID'
    ).values('product_id', 'product__name', 'product__sku', 'product__price').annotate(
        units_sold=Sum('quantity'),
        revenue=Sum('total_price')
    ).order_by('-units_sold')
    
    top_selling_ids = []
    for entry in sales_past_30[:5]:
        insights['top_sellers'].append({
            'name': entry['product__name'],
            'sku': entry['product__sku'],
            'units_sold': entry['units_sold'],
            'revenue': float(entry['revenue'])
        })
        top_selling_ids.append(entry['product_id'])
        
    # Slow movers & Dead Stock
    sold_dict = {entry['product_id']: entry['units_sold'] for entry in sales_past_30}
    
    for p in products:
        units = sold_dict.get(p.id, 0)
        if units == 0 and p.stock_quantity > 0:
            insights['dead_stock'].append({
                'name': p.name,
                'sku': p.sku,
                'stock': p.stock_quantity,
                'value': float(p.price) * p.stock_quantity
            })
        elif 0 < units <= 2 and p.id not in top_selling_ids:
            insights['slow_movers'].append({
                'name': p.name,
                'sku': p.sku,
                'stock': p.stock_quantity,
                'units_sold': units
            })
            
    # Sort slow movers and dead stock
    insights['dead_stock'] = sorted(insights['dead_stock'], key=lambda x: x['value'], reverse=True)[:5]
    insights['slow_movers'] = sorted(insights['slow_movers'], key=lambda x: x['units_sold'])[:5]
    
    return insights

def get_demand_forecasts(business):
    """
    Predict demand, forecast future sales, and suggest restocking amounts for each product.
    """
    forecasts = []
    if not business or not business.forecasting_enabled:
        return forecasts
        
    products = Product.objects.filter(business=business, item_type='PRODUCT')
    
    for p in products:
        avg_daily = get_average_daily_sales(p, days=30)
        recent_avg = get_average_daily_sales(p, days=7) # short term trend
        
        # Weighted forecast: 70% long-term, 30% short-term
        forecast_daily = (0.7 * avg_daily) + (0.3 * recent_avg)
        
        expected_week = forecast_daily * 7.0
        expected_month = forecast_daily * 30.0
        
        # Suggested restocking quantity (buffer of 20%)
        suggested_restock = max(0, int(expected_month * 1.2) - p.stock_quantity)
        
        forecasts.append({
            'product': p,
            'avg_daily_sales': round(avg_daily, 2),
            'expected_sales_next_week': int(expected_week),
            'expected_sales_next_month': int(expected_month),
            'suggested_restock': suggested_restock,
            'status': 'HIGH_DEMAND' if forecast_daily > 1.5 else 'NORMAL'
        })
        
    return forecasts

def send_alert_notifications(business):
    """
    Email notification summary compiling low stock and expiry warnings.
    Utilizes Django's configured Email backend.
    """
    if not business or not business.email:
        return False
        
    insights = get_smart_insights(None, business)
    alerts = insights.get('alerts', [])
    
    if not alerts:
        email_body = f"Hello {business.owner_name or 'Store Owner'},\n\nHere is your Intelligent Operations Alert Digest for {business.name}:\n\n"
        email_body += "✅ All operations are green! No active warnings, low stock alerts, or expired batches were detected today.\n\n"
        email_body += "Best regards,\nRetailPos Intelligence Engine"
        try:
            send_mail(
                subject=f"✅ [All Clear] Operations Alert Digest for {business.name}",
                message=email_body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'intelligence@retailpos.com'),
                recipient_list=[business.email],
                fail_silently=True
            )
            return True
        except Exception:
            return False
            
    email_body = f"Hello {business.owner_name or 'Store Owner'},\n\nHere is your Intelligent Operations Alert Digest for {business.name}:\n\n"
    
    critical_alerts = [a for a in alerts if 'CRITICAL' in a.get('type', '') or 'EXPIRED' in a.get('type', '')]
    warning_alerts = [a for a in alerts if a not in critical_alerts]
    
    if critical_alerts:
        email_body += "⚠️ CRITICAL ALERTS:\n"
        for idx, alert in enumerate(critical_alerts, 1):
            email_body += f"{idx}. {alert['title']}: {alert['message']}\n"
        email_body += "\n"
        
    if warning_alerts:
        email_body += "🔔 WARNING ALERTS:\n"
        for idx, alert in enumerate(warning_alerts, 1):
            email_body += f"{idx}. {alert['title']}: {alert['message']}\n"
        email_body += "\n"
        
    email_body += "Please log in to your RetailPos Dashboard to manage your stock, review dynamic pricing adjustments, and replenish expiring or depleted batches.\n\nBest regards,\nRetailPos Intelligence Engine"
    
    try:
        send_mail(
            subject=f"⚠️ [Alert Digest] Intelligent Stock & Expiry Warnings for {business.name}",
            message=email_body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'intelligence@retailpos.com'),
            recipient_list=[business.email],
            fail_silently=True
        )
        return True
    except Exception:
        return False
