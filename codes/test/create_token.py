#!/usr/bin/env python
"""
Test script to create API token for WebSocket REST API testing
Run this in Django environment: python manage.py shell < test/create_token.py
"""

import os
import sys
import django

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_test_token():
    """Create or get API token for testing"""
    
    # Get or create a user
    user = User.objects.first()
    if not user:
        user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        print(f"Created new user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")

    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    
    if created:
        print(f"Created new API token: {token.key}")
    else:
        print(f"Existing API token: {token.key}")
    
    # Save token to a file for easy access
    token_file = os.path.join(os.path.dirname(__file__), 'api_token.txt')
    with open(token_file, 'w') as f:
        f.write(token.key)
    print(f"Token saved to: {token_file}")
    
    return token.key

if __name__ == "__main__":
    create_test_token()