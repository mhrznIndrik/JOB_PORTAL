from django.shortcuts import render, redirect
from django.http import HttpRequest
from .models import User, PendingUser, Token, TokenType
from django.contrib.auth.hashers import make_password
from django.contrib import messages, auth
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.utils import timezone
from common.tasks import send_email
from django.contrib.auth import get_user_model
from .decorators import redirect_authenticated_user


def home(request: HttpRequest):
    return render(request, 'home.html')

@redirect_authenticated_user
def login(request: HttpRequest):
    if request.method == 'POST':
        email: str = request.POST.get('email')
        password: str = request.POST.get('password')
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')
    
def logout(request: HttpRequest):
    auth.logout(request)
    messages.success(request, 'Logout successful')
    return redirect('home')

@redirect_authenticated_user
def register(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "register.html")

        pending_user = PendingUser.objects.filter(email=email).first()
        if pending_user:
            verification_code = get_random_string(length=6)
            pending_user.verification_code = verification_code
            pending_user.created_at = timezone.now()
            pending_user.save()

            send_email.delay(
                'Verify your account',
                [email],
                'emails/email_verification_template.html',
                context={'code': verification_code}
            )

            messages.info(request, "You already have a pending account. A new verification code has been sent.")
            return render(request, 'verify_account.html', context={'email': email})

        verification_code = get_random_string(length=6)
        PendingUser.objects.create(email=email, password=make_password(password), verification_code=verification_code, created_at=timezone.now())
        

        send_email.delay(
            'Verify your account',
            [email],
            'emails/email_verification_template.html',
            context={'code': verification_code}
        )

        messages.success(request, "Account created! Check your email for the verification code.")
        return render(request, 'verify_account.html', context={'email': email}) 
    return render(request, "register.html")


def verify_account(request):
    email = request.POST.get('email') or request.GET.get('email', '')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()

        if not code:
            messages.error(request, "Please enter the verification code.")
            return render(request, 'verify_account.html', {'email': email})

        pending_user = PendingUser.objects.filter(email=email, verification_code=code).first()

        if pending_user.verification_code == code:
            if not pending_user.is_valid():
                messages.error(request, "Verification code expired. Please resend a new code.")
                return render(request, "verify_account.html", {"email": email})
            
            user = User(email=pending_user.email)
            user.password = pending_user.password 
            user.save()

            pending_user.delete()

            auth.login(request, user)
            messages.success(request, "Account verified!")
            return redirect('home')
        else:
            messages.error(request, "Invalid verification code.")
            return render(request, 'verify_account.html', {'email': email}, status=400)

    email = request.GET.get('email', '')
    return render(request, 'verify_account.html', {'email': email})

def resend_verification(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Email is required to resend verification code.")
            return redirect("verify_account")  

        pending_user = PendingUser.objects.filter(email=email).first()
        if pending_user:
            now = timezone.now()
            cooldown = timedelta(minutes=5)  

            if now - pending_user.created_at < cooldown:
                messages.error(request, "You can request a new code only every 5 minutes.")
                return render(request, "verify_account.html", {"email": email})

            verification_code = get_random_string(length=6)
            pending_user.verification_code = verification_code
            pending_user.created_at = now
            pending_user.save()

            send_email.delay(
                'Verify your account',
                [email],
                'emails/email_verification_template.html',
                context={'code': verification_code}
            )

            messages.success(request, "A new verification code has been sent to your email.")
        else:
            messages.error(request, "No pending account found with this email.")
        
        return render(request, "verify_account.html", {"email": email})
    
def send_password_reset_link(request: HttpRequest):
    if request.method == 'POST':
        email:str = request.POST.get('email', '')
        user = get_user_model().objects.filter(email=email.lower()).first()
        
        if user:
            token, _ = Token.objects.update_or_create(
                user=user,
                token_type = TokenType.PASSWORD_RESET,
                defaults={
                    'token': get_random_string(length=20),
                    'created_at': datetime.now()
                }
            )
            
            email_data = {
                'email': email.lower(),
                'token': token.token
            }
            
            send_email.delay(
                "Your password reset link",
                [email],
                'emails/password_reset_template.html',
                email_data
            )
            messages.success(request, 'Password reset link sent')
            return redirect('forgot_password')
        else:
            messages.error(request, 'Email does not exist')
            return redirect('forgot_password')
        
    else:
        return render(request, 'forgot_password.html')
    
def verify_password_reset_link(request: HttpRequest):
    email = request.GET.get('email')
    reset_token = request.GET.get('token')
    
    token = Token.objects.filter(
        user__email=email,
        token=reset_token,
        token_type=TokenType.PASSWORD_RESET,
    ).first()
    
    if not token or not token.is_valid():
        messages.error(request, 'Invalid link')
        return redirect('forgot_password')
    
    return render(request, 'set_new_password_using_reset_token.html', 
                  context={'email': email, 'token': reset_token}
                  )
    
def set_new_password(request: HttpRequest):
    """Set a new password given the token sent to the user email"""
    
    if request.method == 'POST':
        password1: str = request.POST.get('password1')
        password2: str = request.POST.get('password2')
        email: str = request.POST.get('email')
        reset_token: str = request.POST.get('token')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'set_new_password_using_reset_token.html', 
                          context={'email': email, 'token': reset_token}
                          )
            
        token: Token = Token.objects.filter(
            user__email=email,
            token=reset_token,
            token_type=TokenType.PASSWORD_RESET,
        ).first()
        
        if not token or not token.is_valid():
            messages.error(request, 'Invalid link')
            return redirect('forgot_password')
        
        token.reset_user_password(password1)
        token.delete()
        
        messages.success(request, 'Password reset successful')
        return redirect('login')