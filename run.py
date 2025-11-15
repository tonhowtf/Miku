import os
import django
from threading import Thread
from dotenv import load_dotenv
import subprocess
import time
import sys


load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from django.core.management import call_command

subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)

call_command('collectstatic', '--noinput')

call_command('migrate', '--noinput')

subprocess.run([sys.executable, 'create_user.py'])

def run_django():
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:80', '--noreload'])

if __name__ == '__main__':
    django_thread = Thread(target=run_django, daemon=True)
    django_thread.start()

    time.sleep(3)

    from bot.bot import main
    main()