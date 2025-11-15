import os
import django
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

ADMIN_USER = os.getenv('ADMIN_USER')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASS = os.getenv('ADMIN_PASS')

try:
    user = User.objects.get(username=ADMIN_USER)
    user.is_staff = True
    user.is_superuser = True
    user.email = ADMIN_EMAIL
    user.set_password(ADMIN_PASS)
    user.save()
    
except User.DoesNotExist:
    User.objects.create_superuser(ADMIN_USER, ADMIN_EMAIL, ADMIN_PASS)