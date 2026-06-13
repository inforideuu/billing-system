import os
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from inventory.models import Product, Batch
from billing.models import Invoice, Customer, InvoiceItem
from core.utils import filter_by_business

def route_chatbot_query(user, business, query_text):
    """
    Parse natural language query, respect role boundaries, execute database lookups,
    and formulate a beautifully formatted response.
    """
    query = query_text.lower().strip()
    user_role = getattr(user.profile, 'role', 'CASHIER')
    
    # 1. Enforce Role-based Data Access Control
    restricted_keywords = ['profit', 'margin', 'ledger', 'financial', 'tax', 'all cashiers', 'staff salary', 'subscription']
    is_asking_restricted = any(keyword in query for keyword in restricted_keywords)
    
    if user_role == 'CASHIER' and is_asking_restricted:
        return {
            'message': (
                "⚠️ **Access Restricted:** As a Staff Cashier, you do not have permission "
                "to view global shop profit margins or general ledger summaries. "
                "You can ask me about **low stock products**, **today's sales counts**, "
                "or **look up a product price**!"
            ),
            'is_system_data': False,
            'suggestions': ["Today's sales count", "Low stock products", "Price of mouse"]
        }

    # 2. Today's Sales Intent
    if any(k in query for k in ['today\'s sales', 'today sales', 'sales today', 'revenue today', 'sales count today']):
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        invoices = Invoice.objects.filter(business=business, date__gte=today_start, status='PAID')
        
        # Staff can only see their own sales if restricted, or general sales totals if cashier
        if user_role == 'CASHIER':
            invoices = invoices.filter(user=user)
            
        summary = invoices.aggregate(total=Sum('total_amount'), count=Count('id'))
        total_sales = summary['total'] or 0.00
        sales_count = summary['count'] or 0
        
        msg = f"📊 **Today's Sales Summary:**\n\n"
        if user_role == 'CASHIER':
            msg += f"You have processed **{sales_count} invoices** today for a total of **₹{total_sales:.2f}**."
        else:
            msg += f"Your store processed **{sales_count} invoices** today, generating a total revenue of **₹{total_sales:.2f}**."
            
        return {
            'message': msg,
            'is_system_data': True,
            'data_payload': {
                'total_sales': float(total_sales),
                'invoice_count': sales_count,
                'timeframe': 'Today'
            },
            'suggestions': ["Low stock products", "Pending payments", "Top selling products"]
        }

    # 3. Low Stock Intent
    if any(k in query for k in ['low stock', 'out of stock', 'stock warning', 'run out']):
        low_stock_threshold = business.low_stock_threshold
        products = Product.objects.filter(
            business=business,
            item_type='PRODUCT',
            stock_quantity__lte=low_stock_threshold
        ).order_by('stock_quantity')
        
        if products.exists():
            msg = f"⚠️ **Low Stock Alert (Threshold: {low_stock_threshold} units):**\n\n"
            msg += "| Product Name | SKU | Stock Qty |\n| :--- | :--- | :--- |\n"
            payload_list = []
            for p in products:
                msg += f"| {p.name} | `{p.sku}` | **{p.stock_quantity}** |\n"
                payload_list.append({'name': p.name, 'sku': p.sku, 'stock': p.stock_quantity})
            msg += "\n💡 *Suggested action: Please generate a purchase order soon to replenish these items.*"
            return {
                'message': msg,
                'is_system_data': True,
                'data_payload': payload_list,
                'suggestions': ["Suggest restocking quantity", "Top selling products", "Today's sales"]
            }
        else:
            return {
                'message': "✅ All products are perfectly stocked above your low-stock threshold level!",
                'is_system_data': False,
                'suggestions': ["Top selling products", "Today's sales"]
            }

    # 4. Top Selling Products Intent
    if any(k in query for k in ['top selling', 'best seller', 'most popular', 'top products']):
        cutoff_30 = timezone.now() - timedelta(days=30)
        sales = InvoiceItem.objects.filter(
            product__business=business,
            invoice__date__gte=cutoff_30,
            invoice__status='PAID'
        ).values('product_id', 'product__name', 'product__sku').annotate(
            units_sold=Sum('quantity'),
            revenue=Sum('total_price')
        ).order_by('-units_sold')[:5]
        
        if sales.exists():
            msg = "🔥 **Top 5 Selling Products (Last 30 Days):**\n\n"
            msg += "| Rank | Product Name | Units Sold | Total Revenue |\n| :---: | :--- | :---: | :---: |\n"
            payload_list = []
            for idx, entry in enumerate(sales, 1):
                msg += f"| {idx} | {entry['product__name']} | **{entry['units_sold']}** | ₹{entry['revenue']:.2f} |\n"
                payload_list.append({
                    'rank': idx,
                    'name': entry['product__name'],
                    'units_sold': entry['units_sold'],
                    'revenue': float(entry['revenue'])
                })
            return {
                'message': msg,
                'is_system_data': True,
                'data_payload': payload_list,
                'suggestions': ["Low stock products", "Pending payments", "Last month report"]
            }
        else:
            return {
                'message': "No sales recorded in the past 30 days. Let's record some invoice checkouts!",
                'is_system_data': False,
                'suggestions': ["Low stock products", "Today's sales"]
            }

    # 5. Pending Payments Intent
    if any(k in query for k in ['pending payment', 'unpaid', 'pending invoices', 'debts']):
        invoices = Invoice.objects.filter(business=business, status='PENDING').order_by('-date')
        
        if invoices.exists():
            count = invoices.count()
            total_pending = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0.00
            msg = f"⏳ **Pending Invoices Alert:**\n"
            msg += f"There are currently **{count} pending invoices** awaiting cash/UPI clearance, totaling **₹{total_pending:.2f}**.\n\n"
            msg += "| Bill No | Customer | Date | Amount |\n| :--- | :--- | :---: | :---: |\n"
            payload_list = []
            for inv in invoices[:5]:
                cust_name = inv.customer.name if inv.customer else 'Walk-in'
                msg += f"| INV-{inv.id} | {cust_name} | {inv.date.strftime('%Y-%m-%d')} | **₹{inv.total_amount:.2f}** |\n"
                payload_list.append({'id': inv.id, 'customer': cust_name, 'date': str(inv.date.date()), 'amount': float(inv.total_amount)})
            if count > 5:
                msg += f"| ... | and {count-5} more items | ... | ... |\n"
            return {
                'message': msg,
                'is_system_data': True,
                'data_payload': payload_list,
                'suggestions': ["Today's sales", "Low stock products", "Top selling products"]
            }
        else:
            return {
                'message': "🎉 Excellent! There are no pending or unpaid invoices on the system.",
                'is_system_data': False,
                'suggestions': ["Today's sales", "Low stock products"]
            }

    # 6. Last Month Report Intent
    if any(k in query for k in ['last month report', 'previous month', 'monthly summary', 'report last month']):
        # Access control check
        if user_role == 'CASHIER':
            return {
                'message': "⚠️ **Access Restricted:** Detailed historical ledger summaries are restricted to store Administrators.",
                'is_system_data': False,
                'suggestions': ["Today's sales", "Low stock products"]
            }
            
        today = date.today()
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        invoices = Invoice.objects.filter(
            business=business,
            date__date__gte=last_month_start,
            date__date__lte=last_month_end,
            status='PAID'
        )
        
        summary = invoices.aggregate(
            total_sales=Sum('total_amount'),
            tax=Sum('gst_amount'),
            count=Count('id')
        )
        
        total_rev = summary['total_sales'] or 0.00
        total_tax = summary['tax'] or 0.00
        inv_count = summary['count'] or 0
        avg_basket = float(total_rev) / float(inv_count) if inv_count > 0 else 0.00
        
        msg = (
            f"📅 **Sales Ledger Report (Last Month: {last_month_start.strftime('%B %Y')}):**\n\n"
            f"📈 **Total Revenue Generated:** ₹{total_rev:.2f}\n"
            f"💼 **Tax Collected (GST):** ₹{total_tax:.2f}\n"
            f"🧾 **Invoices Processed:** {inv_count} bills\n"
            f"🛒 **Average Invoice Value:** ₹{avg_basket:.2f}\n\n"
            f"💡 *Insights: Average basket size indicates robust checkout activity.*"
        )
        
        return {
            'message': msg,
            'is_system_data': True,
            'data_payload': {
                'revenue': float(total_rev),
                'tax': float(total_tax),
                'bills': inv_count,
                'average': avg_basket
            },
            'suggestions': ["Top selling products", "Low stock products", "Today's sales"]
        }

    # 7. Restocking suggestions
    if any(k in query for k in ['restock', 'replenish', 'suggest restock', 'restocking guide']):
        from .utils import get_demand_forecasts
        forecasts = get_demand_forecasts(business)
        restock_needed = [f for f in forecasts if f['suggested_restock'] > 0]
        
        if restock_needed:
            msg = "📋 **Restocking Quantity Recommendations:**\n\n"
            msg += "| Product | Current Stock | Forecast Sales (30d) | Restock Quantity |\n| :--- | :---: | :---: | :---: |\n"
            payload_list = []
            for f in restock_needed[:5]:
                msg += f"| {f['product'].name} | {f['product'].stock_quantity} | {f['expected_sales_next_month']} units | **+{f['suggested_restock']}** |\n"
                payload_list.append({'name': f['product'].name, 'stock': f['product'].stock_quantity, 'forecast': f['expected_sales_next_month'], 'suggested': f['suggested_restock']})
            return {
                'message': msg,
                'is_system_data': True,
                'data_payload': payload_list,
                'suggestions': ["Low stock products", "Today's sales"]
            }
        else:
            return {
                'message': "✅ Current stock quantities are completely sufficient to cover next month's predicted sales demand!",
                'is_system_data': False,
                'suggestions': ["Today's sales", "Top selling products"]
            }

    # 8. Look up product details/pricing
    if any(k in query for k in ['price of', 'look up', 'search product', 'find stock']):
        # Extract product name candidates
        clean_query = query.replace('price of', '').replace('look up', '').replace('search', '').replace('find', '').replace('product', '').strip()
        if len(clean_query) >= 3:
            products = Product.objects.filter(business=business, name__icontains=clean_query)
            if products.exists():
                msg = "🔍 **Product Lookup Results:**\n\n"
                msg += "| Name | SKU | Price | Stock |\n| :--- | :--- | :---: | :---: |\n"
                payload_list = []
                for p in products[:5]:
                    msg += f"| {p.name} | `{p.sku}` | ₹{p.price:.2f} | {p.stock_quantity} units |\n"
                    payload_list.append({'name': p.name, 'sku': p.sku, 'price': float(p.price), 'stock': p.stock_quantity})
                return {
                    'message': msg,
                    'is_system_data': True,
                    'data_payload': payload_list,
                    'suggestions': ["Low stock products", "Today's sales"]
                }
                
        return {
            'message': f"I couldn't locate any products matching '{clean_query}'. Please try typing the exact name.",
            'is_system_data': False,
            'suggestions': ["Low stock products", "Today's sales"]
        }

    # 9. Fallback general conversational responses (with LLM simulation or Gemini integration)
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        import requests
        import json
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        headers = {'Content-Type': 'application/json'}
        prompt = (
            f"You are the intelligent assistant for the RetailPos Billing Platform. "
            f"A user ({user.username}, role: {user_role}) asks: '{query_text}'. "
            f"The business is '{business.name}'. "
            f"Provide a friendly, highly concise (max 3 sentences) response. "
            f"Do not mention passwords or restricted files."
        )
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 150}
        }
        try:
            res = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
            if res.status_code == 200:
                ai_text = res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                return {
                    'message': ai_text,
                    'is_system_data': False,
                    'suggestions': ["Today's sales", "Low stock products", "Pending payments"]
                }
        except Exception:
            pass # fallback to local conversational engine

    # Local natural conversational responder (Fallback)
    greetings = ['hi', 'hello', 'hey', 'greetings', 'help', 'who are you']
    if any(g in query for g in greetings):
        return {
            'message': (
                f"👋 Hello **{user.username}**! I am your **RetailPos AI Assistant**.\n\n"
                "I can fetch live data for you in real-time. Try asking me:\n"
                "* 📊 *'Show today's sales'*\n"
                "* ⚠️ *'Which products are low in stock?'*\n"
                "* ⏳ *'Are there any pending payments?'*\n"
                "* 🔥 *'What are our top selling products?'*\n\n"
                "How can I assist you in your shop operations today?"
            ),
            'is_system_data': False,
            'suggestions': ["Today's sales", "Low stock products", "Pending payments"]
        }
        
    return {
        'message': (
            "I couldn't quite map that request to a database report. "
            "Try asking one of our standard business queries: "
            "**Today's sales**, **Low stock warnings**, **Top selling items**, "
            "or **Pending payments**!"
        ),
        'is_system_data': False,
        'suggestions': ["Today's sales", "Low stock products", "Pending payments"]
    }
