import os
import django
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
call_command('collectstatic', '--noinput')
call_command('migrate', '--noinput')

def run_bot():
    from bot.bot import main
    main()

def run_django():
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:80'])

if __name__ == '__main__':
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    run_django()