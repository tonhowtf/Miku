import os
import django
from threading import Thread
from dotenv import load_dotenv
import subprocess
import time
import sys

subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
call_command('collectstatic', '--noinput')
call_command('migrate', '--noinput')

def run_django():
    import subprocess
    subprocess.run([
        sys.executable,
        '-m'
        'daphne',
        '-b', '0.0.0.0',
        '-p', '80',
        'config.asgi:application'
    ])

if __name__ == '__main__':
    django_thread = Thread(target=run_django, daemon=True)
    django_thread.start()

    time.sleep(15)

    from bot.bot import main
    
    main()