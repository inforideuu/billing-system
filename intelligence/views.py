from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.decorators import role_required, plan_feature_required
from core.utils import filter_by_business, get_business
from inventory.models import Product, Batch
from .utils import get_smart_insights, get_demand_forecasts, send_alert_notifications, get_dynamic_price

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
@plan_feature_required('has_smart_insights')
def insights(request):
    business = get_business(request)
    insights_data = get_smart_insights(request, business)
    forecasts = get_demand_forecasts(business)
    
    # Filter products for UI selections
    products = filter_by_business(Product.objects.filter(item_type='PRODUCT'), request)
    
    context = {
        'business': business,
        'alerts': insights_data['alerts'],
        'sales_performance': insights_data['sales_performance'],
        'top_sellers': insights_data['top_sellers'],
        'slow_movers': insights_data['slow_movers'],
        'dead_stock': insights_data['dead_stock'],
        'forecasts': forecasts,
        'products': products
    }
    return render(request, 'intelligence/insights.html', context)

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
@plan_feature_required('has_batch_tracking')
def batches_list(request):
    business = get_business(request)
    batches = filter_by_business(Batch.objects.all(), request).order_by('expiry_date')
    products = filter_by_business(Product.objects.filter(item_type='PRODUCT'), request).order_by('name')
    
    from datetime import date, timedelta
    today = date.today()
    expiry_threshold = today + timedelta(days=business.expiry_alert_days)
    
    context = {
        'business': business,
        'batches': batches,
        'products': products,
        'today': today,
        'expiry_threshold': expiry_threshold
    }
    return render(request, 'intelligence/batches.html', context)

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
@plan_feature_required('has_batch_tracking')
def add_batch(request):
    if request.method == 'POST':
        try:
            business = get_business(request)
            product_id = request.POST.get('product_id')
            product = get_object_or_404(filter_by_business(Product.objects.all(), request), id=product_id)
            
            batch_num = request.POST.get('batch_number', '').strip()
            mfg_date = request.POST.get('manufacture_date')
            exp_date = request.POST.get('expiry_date')
            stock_qty = int(request.POST.get('stock_quantity', 0))
            
            if not batch_num or not exp_date:
                return JsonResponse({'status': 'error', 'message': 'Batch number and expiry date are required.'})
                
            batch = Batch.objects.create(
                business=business,
                product=product,
                batch_number=batch_num,
                manufacture_date=mfg_date if mfg_date else None,
                expiry_date=exp_date,
                stock_quantity=stock_qty,
                initial_quantity=stock_qty
            )
            
            # Sync product's overall stock quantity!
            product.stock_quantity = sum(b.stock_quantity for b in product.batches.all())
            product.save()
            
            return JsonResponse({'status': 'success', 'batch_id': batch.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
@plan_feature_required('has_batch_tracking')
def delete_batch(request, batch_id):
    if request.method == 'POST':
        try:
            batch = get_object_or_404(filter_by_business(Batch.objects.all(), request), id=batch_id)
            product = batch.product
            batch.delete()
            
            # Recalculate product stock
            product.stock_quantity = sum(b.stock_quantity for b in product.batches.all())
            product.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def edit_settings(request):
    business = get_business(request)
    plan = business.subscription_plan
    
    if request.method == 'POST':
        try:
            # Check features allowed by the active plan
            has_smart_insights = plan.has_smart_insights if plan else False
            has_forecasting = plan.has_forecasting if plan else False
            has_dynamic_pricing = plan.has_dynamic_pricing if plan else False
            has_batch_tracking = plan.has_batch_tracking if plan else False
            
            # Update only enabled features according to plan limits
            if has_smart_insights:
                business.smart_insights_enabled = request.POST.get('smart_insights') == 'on'
            else:
                business.smart_insights_enabled = False
                
            if has_forecasting:
                business.forecasting_enabled = request.POST.get('forecasting') == 'on'
            else:
                business.forecasting_enabled = False
                
            if has_dynamic_pricing:
                business.dynamic_pricing_enabled = request.POST.get('dynamic_pricing') == 'on'
            else:
                business.dynamic_pricing_enabled = False
                
            if has_batch_tracking:
                business.batch_tracking_enabled = request.POST.get('batch_tracking') == 'on'
            else:
                business.batch_tracking_enabled = False
            
            business.low_stock_threshold = int(request.POST.get('low_stock_threshold', 5))
            
            if has_batch_tracking:
                business.expiry_alert_days = int(request.POST.get('expiry_alert_days', 30))
            
            if has_dynamic_pricing:
                business.pricing_low_stock_percent = float(request.POST.get('pricing_low_stock_percent', 10))
                business.pricing_high_demand_percent = float(request.POST.get('pricing_high_demand_percent', 15))
                business.pricing_clearance_percent = float(request.POST.get('pricing_clearance_percent', 20))
            
            business.save()
            messages.success(request, "Intelligence settings updated successfully!")
            return redirect('intelligence_settings')
        except Exception as e:
            messages.error(request, f"Error updating settings: {str(e)}")
            
    return render(request, 'intelligence/settings.html', {'business': business})

@login_required(login_url='/accounts/login/')
@role_required(['ADMIN'])
def trigger_notifications(request):
    if request.method == 'POST':
        business = get_business(request)
        if not business.email:
            return JsonResponse({'status': 'error', 'message': 'Please configure a valid shop email in Business settings.'})
            
        success = send_alert_notifications(business)
        if success:
            return JsonResponse({'status': 'success', 'message': f'Alert summary digest emailed successfully to {business.email}.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Failed to dispatch email. No active warnings found or mail server offline.'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'})

@login_required(login_url='/accounts/login/')
def api_get_notifications(request):
    """
    Returns the real-time operational alerts (low stock, expiring soon) 
    for the global notification dropdown panel.
    """
    business = get_business(request)
    if not business:
        return JsonResponse({'status': 'error', 'message': 'No active business.'})
        
    insights = get_smart_insights(request, business)
    alerts = insights.get('alerts', [])
    
    return JsonResponse({'status': 'success', 'count': len(alerts), 'alerts': alerts})

@login_required(login_url='/accounts/login/')
def api_dismiss_alert(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            alert_key = data.get('alert_key')
            business = get_business(request)
            if business and alert_key:
                from .models import DismissedAlert
                DismissedAlert.objects.get_or_create(business=business, alert_key=alert_key)
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# AI Chatbot API Endpoints
from django.utils import timezone
from datetime import timedelta
import json
from .models import ChatSession, ChatMessage
from .chatbot_engine import route_chatbot_query

@login_required(login_url='/accounts/login/')
def chat_sessions_list(request):
    """
    Returns the list of active chat sessions for the logged-in user under their business.
    """
    business = get_business(request)
    sessions = ChatSession.objects.filter(business=business, user=request.user).order_by('-created_at')
    
    session_list = []
    for s in sessions[:10]: # Return top 10 conversations
        session_list.append({
            'id': s.id,
            'title': s.title,
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'status': 'success', 'sessions': session_list})

@login_required(login_url='/accounts/login/')
def chat_session_messages(request, session_id):
    """
    Returns the message history for a specific chat session thread.
    """
    business = get_business(request)
    session = get_object_or_404(ChatSession, id=session_id, business=business, user=request.user)
    
    messages = session.messages.all().order_by('timestamp')
    msg_list = []
    for m in messages:
        msg_list.append({
            'sender': m.sender,
            'message': m.message,
            'is_system_data': m.is_system_data,
            'data_payload': m.data_payload,
            'timestamp': m.timestamp.strftime('%H:%M')
        })
    return JsonResponse({'status': 'success', 'messages': msg_list})

@login_required(login_url='/accounts/login/')
def post_chat_message(request):
    """
    Submit a message to the chatbot. If no active session is selected, starts a new thread.
    """
    if request.method == 'POST':
        try:
            business = get_business(request)
            data = json.loads(request.body)
            user_msg = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not user_msg:
                return JsonResponse({'status': 'error', 'message': 'Message body cannot be empty.'})
                
            # Rate limiting: Max 30 messages/minute per user
            one_minute_ago = timezone.now() - timedelta(minutes=1)
            recent_count = ChatMessage.objects.filter(
                session__user=request.user,
                timestamp__gte=one_minute_ago,
                sender='USER'
            ).count()
            
            if recent_count >= 30:
                return JsonResponse({
                    'status': 'error', 
                    'message': '⚠️ Rate limit exceeded. Please wait a moment before sending more messages.'
                })
            
            # Resolve or create ChatSession
            if session_id:
                session = get_object_or_404(ChatSession, id=session_id, business=business, user=request.user)
            else:
                title = user_msg[:30] + '...' if len(user_msg) > 30 else user_msg
                session = ChatSession.objects.create(
                    business=business,
                    user=request.user,
                    title=title
                )
                
            # 1. Save User query to DB
            ChatMessage.objects.create(
                session=session,
                sender='USER',
                message=user_msg
            )
            
            # 2. Process using Cognitive Query intent engine
            response_data = route_chatbot_query(request.user, business, user_msg)
            
            # 3. Save AI Response to DB
            ChatMessage.objects.create(
                session=session,
                sender='AI',
                message=response_data['message'],
                is_system_data=response_data.get('is_system_data', False),
                data_payload=response_data.get('data_payload')
            )
            
            return JsonResponse({
                'status': 'success',
                'session_id': session.id,
                'session_title': session.title,
                'message': response_data['message'],
                'is_system_data': response_data.get('is_system_data', False),
                'data_payload': response_data.get('data_payload'),
                'suggestions': response_data.get('suggestions', ["Today's sales", "Low stock products"]),
                'timestamp': timezone.now().strftime('%H:%M')
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid method.'})

