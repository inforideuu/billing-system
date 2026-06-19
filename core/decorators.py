from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/accounts/login/')
            
            # Safety check in case signal failed
            if not hasattr(request.user, 'profile'):
                from core.models import UserProfile
                UserProfile.objects.get_or_create(user=request.user, defaults={'role': 'SUPER_ADMIN' if request.user.is_superuser else 'CASHIER'})
                
            if request.user.profile.role in allowed_roles or request.user.is_superuser or request.user.profile.role == 'SUPER_ADMIN':
                return view_func(request, *args, **kwargs)
            
            # Non-authorized response
            messages.error(request, "Access Denied: Insufficient privileges to view this module.")
            return redirect('dashboard') # Fallback to dashboard
        return _wrapped_view
    return decorator

def plan_feature_required(feature_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/accounts/login/')
            
            # Super Admins have absolute full access
            if hasattr(request.user, 'profile') and request.user.profile.role == 'SUPER_ADMIN':
                return view_func(request, *args, **kwargs)
                
            if hasattr(request.user, 'profile') and request.user.profile.business:
                business = request.user.profile.business
                plan = business.subscription_plan
                if plan:
                    if getattr(plan, feature_name, False):
                        return view_func(request, *args, **kwargs)
                
                messages.error(request, f"Plan Upgrade Required: The requested module is not available in your current plan. Please upgrade your plan to unlock it.")
                return redirect('subscription_purchase')
            
            messages.error(request, "Access Denied: Shop context not found.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator
