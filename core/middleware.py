from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

class BusinessStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Skip check for Super Admins explicitly
            if hasattr(request.user, 'profile') and request.user.profile.role == 'SUPER_ADMIN':
                return self.get_response(request)
            
            # Check if user has a profile and business
            if hasattr(request.user, 'profile') and request.user.profile.business:
                business = request.user.profile.business
                
                # Check if explicitly blocked by Super Admin
                if not business.is_subscription_active:
                    allowed_names = ['logout', 'login', 'subscription_expired']
                    allowed_paths = []
                    for name in allowed_names:
                        try:
                            allowed_paths.append(reverse(name))
                        except Exception:
                            pass
                    allowed_paths.extend(['/accounts/logout/', '/accounts/login/'])
                    if request.path not in allowed_paths and not request.path.startswith('/admin/'):
                        return redirect('subscription_expired')
                    return self.get_response(request)

                # Check expiration dynamically
                is_expired = False
                if business.subscription_end_date and business.subscription_end_date < timezone.now():
                    is_expired = True
                    if business.subscription_plan is not None:
                        business.subscription_plan = None
                        business.is_subscription_active = False
                        business.save()
                
                has_no_plan = not business.subscription_plan or is_expired
                
                if has_no_plan:
                    # Allow access to logout, login, and subscription renewal URLs
                    allowed_names = [
                        'logout', 'login', 
                        'subscription_purchase', 
                        'subscription_checkout', 
                        'payment_callback', 
                        'subscription_expired'
                    ]
                    allowed_paths = []
                    for name in allowed_names:
                        try:
                            allowed_paths.append(reverse(name))
                        except Exception:
                            pass
                    
                    # Add standard django logout paths just in case
                    allowed_paths.extend(['/accounts/logout/', '/accounts/login/', '/subscription/payment-callback/'])
                    
                    if request.path not in allowed_paths and not request.path.startswith('/admin/') and not request.path.startswith('/subscription/checkout/'):
                        user_role = getattr(request.user.profile, 'role', '')
                        if user_role == 'ADMIN':
                            return redirect('subscription_purchase')
                        else:
                            return redirect('subscription_expired')
        
        return self.get_response(request)
