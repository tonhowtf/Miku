import os
import django
from threading import Thread
from dotenv import load_dotenv
import subprocess
import time
import sys
from threading import Thread

subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
subprocess.run([sys.executable, '-m', 'django', 'collectstatic', '--noinput'])

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
call_command('migrate', '--noinput')

subprocess.run([sys.executable, 'create_user.py'])

def run_bot():
    from bot.bot import main
    main()

if __name__ == '__main__':
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()

    time.sleep(3)

    gunicorn_path = "/application/.local/bin/gunicorn"
    subprocess.run([
        gunicorn_path,
        "config.wsgi:application",
        "--bind", "0.0.0.0:80",
        "--log-level", "info"
    ])