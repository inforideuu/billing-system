from django.contrib.auth.forms import AuthenticationForm
from django import forms

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # Call the parent's check (which checks is_active)
        super().confirm_login_allowed(user)
        
        # Super Admins bypass this check
        if hasattr(user, 'profile') and user.profile.role == 'SUPER_ADMIN':
            return
            
        # Check if the user's business is active
        if hasattr(user, 'profile') and user.profile.business:
            if not user.profile.business.is_subscription_active:
                raise forms.ValidationError(
                    f"Access Denied: The subscription for '{user.profile.business.name}' is currently inactive. Please contact system administration.",
                    code='inactive_business',
                )


from django.contrib.auth.models import User
from .models import DemoRequest

class DemoRequestForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), min_length=6, help_text="At least 6 characters")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = DemoRequest
        fields = ['business_name', 'owner_name', 'email', 'phone', 'username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken by an active account.")
        if DemoRequest.objects.filter(username__iexact=username, status='PENDING').exists():
            raise forms.ValidationError("A demo request with this username is already pending approval.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        if DemoRequest.objects.filter(email__iexact=email, status='PENDING').exists():
            raise forms.ValidationError("A demo request with this email is already pending approval.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

