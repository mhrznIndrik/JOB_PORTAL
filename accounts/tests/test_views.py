from django.urls import reverse
from accounts.models import PendingUser, Token, TokenType
from django.contrib.auth.hashers import check_password
from django.contrib.messages import get_messages
from django.contrib.messages.storage.base import Message
from django.test.client import Client
import pytest
from django.contrib.auth import get_user, get_user_model
from datetime import datetime, timezone


pytestmark = pytest.mark.django_db

def test_register_user(client: Client):  # <-- remove : Client
    url = reverse('register')
    request_data = {
        'email': 'abc@gmail.com',
        'password': '12345678'
    }

    response = client.post(url, request_data)

    # In most registration flows, the view redirects after success.
    assert response.status_code in [200, 302]

    # Verify a pending user entry was created
    pending_user = PendingUser.objects.filter(email=request_data['email']).first()
    assert pending_user is not None
    assert check_password(request_data['password'], pending_user.password)
    
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert 'Verification code sent to' in messages[0].message
    assert request_data['email'] in messages[0].message

    
    
def test_register_user_duplicate_email(client: Client, user_instance):
    url = reverse('register')
    request_data = {
        'email': user_instance.email,
        'password': '12345678'
    }
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert response.url == reverse('register')
    
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert 'Email already exists' in str(messages[0])
    
def test_verify_account_valid_code(client: Client):
    pending_user = PendingUser.objects.create(
        email='abc@gmail.com',
        verification_code='8888',
        password='randompass',
    )
    url = reverse('verify_account')
    request_data = {
        'email': pending_user.email,
        'code': pending_user.verification_code
    }
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert response.url == reverse('home')
    user = get_user(response.wsgi_request)
    assert user.is_authenticated
    
    
def test_verify_account_invalid_code(client: Client):
    User = get_user_model()
    pending_user = PendingUser.objects.create(
        email='abc@gmail.com',
        verification_code='8888',
        password='randompass',
    )
    url = reverse('verify_account')
    request_data = {
        'email': pending_user.email,
        'code': 'invalid_code'
    }
    response = client.post(url, request_data)
    assert response.status_code == 400
    assert User.objects.count() == 0
    
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'

def test_login_valid_credentials(client: Client, user_instance, auth_user_password):
    url = reverse('login')
    request_data = {
        'email': user_instance.email,
        'password': auth_user_password
    }
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert response.url == reverse('home')
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'success'
    
def test_login_invalid_credentials(client: Client, user_instance):
    url = reverse('login')
    request_data = {
        'email': user_instance.email,
        'password': 'randominvalidpass'
    }
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert response.url == reverse('login')
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert 'Invalid credentials' in str(messages[0])
    
def test_initiate_password_reset_using_registered_email(client: Client, user_instance):
    url = reverse('forgot_password')
    request_data = {'email': user_instance.email}
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert Token.objects.filter(
        user__email=request_data['email'],
        token_type=TokenType.PASSWORD_RESET
    ).exists()
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'success'
    assert "Password reset link sent" in messages[0].message
    
def test_initiate_password_reset_using_registered_email(client: Client):
    url = reverse('forgot_password')
    request_data = {'email': 'notregistered@gmail.com'}
    response = client.post(url, request_data)
    assert response.status_code == 302
    
    assert not Token.objects.filter(
        user__email=request_data['email'],
        token_type=TokenType.PASSWORD_RESET
    ).first()
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert "Email does not exist" in messages[0].message
    
def test_set_new_password_using_valid_reset_token(client: Client, user_instance):
    url = reverse('set_new_password')
    reset_token = Token.objects.create(
        user=user_instance,
        token_type=TokenType.PASSWORD_RESET,
        token = 'abcd',
        created_at = datetime.now(timezone.utc)
    )
    request_data = {
        'password1': 'newpassword',
        'password2': 'newpassword',
        'email': user_instance.email,
        'token': reset_token.token,
    }
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert response.url == reverse('login')
    assert Token.objects.count() == 0
    
    user_instance.refresh_from_db()
    assert user_instance.check_password(request_data['password1'])
    
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'success'
    assert "Password reset successful" in messages[0].message
    
    
def test_set_new_password_using_invalid_reset_token(client: Client, user_instance):
    url = reverse('set_new_password')
    reset_token = Token.objects.create(
        user=user_instance,
        token_type=TokenType.PASSWORD_RESET,
        token = 'abcd',
        created_at = datetime.now(timezone.utc)
    )
    request_data = {
        'password1': 'newpassword',
        'password2': 'newpassword',
        'email': user_instance.email,
        'token': "invalid_token",
    }
    
    response = client.post(url, request_data)
    assert response.status_code == 302
    assert response.url == reverse('forgot_password')
    assert Token.objects.count() == 1
    
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert "Invalid link" in messages[0].message